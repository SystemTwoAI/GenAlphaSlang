"""
Multi-turn conversation evaluation framework.

Allows evaluators to respond turn-by-turn with either:
1. Free-form text responses
2. Selection from provided multiple-choice options

Author: Manisha Mehta (manisha.mehta@systemtwoai.com)
Date: November 2025
"""

import json
from typing import List, Dict, Optional, Tuple, Union
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
import uuid

from genalpha_converter import GenAlphaConverter


@dataclass
class ResponseOption:
    """A multiple-choice response option."""
    id: str
    text: str
    label: str = ""  # Optional label like "Empathetic", "Directive", etc.
    metadata: Dict = field(default_factory=dict)


@dataclass
class Turn:
    """A single conversation turn."""
    turn_number: int
    speaker: str  # 'patient' or 'therapist'
    text: str
    is_genalpha: bool = False  # Whether this uses GenAlpha language


@dataclass
class EvaluationTurn:
    """A turn in the evaluation with response options."""
    turn_number: int
    patient_message: str
    is_genalpha: bool = False

    # Response options
    response_options: List[ResponseOption] = field(default_factory=list)

    # Allow free-form response
    allow_free_form: bool = True

    # Context: previous conversation history
    conversation_history: List[Turn] = field(default_factory=list)


@dataclass
class EvaluatorResponse:
    """An evaluator's response to a turn."""
    turn_number: int
    response_type: str  # 'free_form' or 'multiple_choice'
    response_text: str
    selected_option_id: Optional[str] = None
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    response_time_seconds: Optional[float] = None
    metadata: Dict = field(default_factory=dict)


@dataclass
class EvaluationSession:
    """A complete evaluation session."""
    session_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    conversation_id: str = ""
    evaluator_id: str = ""
    evaluator_type: str = ""  # 'human', 'claude', 'gpt4', etc.

    # Conversation details
    is_genalpha_version: bool = False
    max_turns: int = 0

    # Responses
    responses: List[EvaluatorResponse] = field(default_factory=list)

    # Metadata
    started_at: str = field(default_factory=lambda: datetime.now().isoformat())
    completed_at: Optional[str] = None
    status: str = "in_progress"  # 'in_progress', 'completed', 'abandoned'

    def add_response(self, response: EvaluatorResponse):
        """Add an evaluator response."""
        self.responses.append(response)

        # Update completion status
        if len(self.responses) >= self.max_turns:
            self.completed_at = datetime.now().isoformat()
            self.status = "completed"

    def get_conversation_so_far(self) -> List[Turn]:
        """Get the conversation reconstructed from responses."""
        turns = []

        # This would need the original patient messages to reconstruct
        # For now, return what we have from responses
        for i, response in enumerate(self.responses):
            # Would need patient turn here
            turns.append(Turn(
                turn_number=i * 2 + 2,  # Therapist turns are even
                speaker='therapist',
                text=response.response_text,
                is_genalpha=False
            ))

        return turns

    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)


class MultiTurnEvaluator:
    """
    Framework for conducting multi-turn conversation evaluations.

    Supports both free-form responses and multiple-choice selection.
    """

    def __init__(self, output_dir: Path):
        """
        Initialize the evaluator.

        Args:
            output_dir: Directory to save evaluation sessions
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.current_session: Optional[EvaluationSession] = None

    def create_evaluation_turns(
        self,
        conversation: List[Dict],
        max_turns: int = 5,
        generate_options: bool = True,
        num_options: int = 3,
        is_genalpha: bool = False,
        genalpha_intensity: float = 0.7
    ) -> List[EvaluationTurn]:
        """
        Create evaluation turns from a conversation.

        Args:
            conversation: Parsed conversation (list of {from, value} dicts)
            max_turns: Maximum number of turns to evaluate
            generate_options: Whether to generate multiple-choice options
            num_options: Number of options to generate per turn
            is_genalpha: Whether to convert patient messages to GenAlpha slang
            genalpha_intensity: Intensity of GenAlpha conversion (0.0-1.0)

        Returns:
            List of EvaluationTurn objects
        """
        # Initialize GenAlpha converter if needed
        converter = None
        if is_genalpha:
            converter = GenAlphaConverter(intensity=genalpha_intensity, use_llm=False)

        # Extract patient turns
        patient_turns = [
            (i, msg) for i, msg in enumerate(conversation)
            if msg.get('from') == 'human'
        ]

        evaluation_turns = []

        for turn_idx, (original_idx, patient_msg) in enumerate(patient_turns[:max_turns]):
            # Get patient message and optionally convert to GenAlpha
            patient_text = patient_msg.get('value', '')
            if is_genalpha and converter:
                patient_text = converter.convert_text(patient_text, context="patient")

            # Build conversation history up to this point
            history = []
            for i, msg in enumerate(conversation[:original_idx + 1]):
                msg_text = msg.get('value', '')
                # Also convert patient messages in history if GenAlpha mode
                if is_genalpha and converter and msg.get('from') == 'human':
                    msg_text = converter.convert_text(msg_text, context="patient")

                history.append(Turn(
                    turn_number=i,
                    speaker='patient' if msg.get('from') == 'human' else 'therapist',
                    text=msg_text,
                    is_genalpha=(is_genalpha and msg.get('from') == 'human')
                ))

            # Create evaluation turn
            eval_turn = EvaluationTurn(
                turn_number=turn_idx + 1,
                patient_message=patient_text,
                conversation_history=history,
                allow_free_form=True,
                is_genalpha=is_genalpha
            )

            # Generate response options if requested
            if generate_options:
                # Get the actual therapist response from the dataset
                actual_response = None
                if original_idx + 1 < len(conversation):
                    next_msg = conversation[original_idx + 1]
                    if next_msg.get('from') == 'gpt':
                        actual_response = next_msg.get('value', '')

                if actual_response:
                    # Use actual response as one option
                    eval_turn.response_options.append(ResponseOption(
                        id=f"option_actual_{turn_idx}",
                        text=actual_response,
                        label="Original Response"
                    ))

                    # Would generate alternative responses here
                    # For now, placeholder
                    for i in range(num_options - 1):
                        eval_turn.response_options.append(ResponseOption(
                            id=f"option_{turn_idx}_{i}",
                            text=f"[Alternative response {i+1} would go here]",
                            label=f"Alternative {i+1}"
                        ))

            evaluation_turns.append(eval_turn)

        return evaluation_turns

    def start_session(
        self,
        conversation_id: str,
        evaluator_id: str,
        evaluator_type: str,
        evaluation_turns: List[EvaluationTurn],
        is_genalpha: bool = False
    ) -> EvaluationSession:
        """
        Start a new evaluation session.

        Args:
            conversation_id: ID of the conversation being evaluated
            evaluator_id: ID of the evaluator (human ID or model name)
            evaluator_type: Type of evaluator ('human', 'claude', 'gpt4', etc.)
            evaluation_turns: List of turns to evaluate
            is_genalpha: Whether this is the GenAlpha version

        Returns:
            New EvaluationSession
        """
        session = EvaluationSession(
            conversation_id=conversation_id,
            evaluator_id=evaluator_id,
            evaluator_type=evaluator_type,
            is_genalpha_version=is_genalpha,
            max_turns=len(evaluation_turns)
        )

        self.current_session = session
        return session

    def submit_response(
        self,
        turn_number: int,
        response_text: str,
        response_type: str = 'free_form',
        selected_option_id: Optional[str] = None,
        response_time_seconds: Optional[float] = None,
        metadata: Optional[Dict] = None
    ) -> EvaluatorResponse:
        """
        Submit a response for a turn.

        Args:
            turn_number: Turn number being responded to
            response_text: The response text
            response_type: 'free_form' or 'multiple_choice'
            selected_option_id: ID of selected option (if multiple choice)
            response_time_seconds: Time taken to respond
            metadata: Additional metadata

        Returns:
            EvaluatorResponse object
        """
        if not self.current_session:
            raise ValueError("No active session. Call start_session() first.")

        response = EvaluatorResponse(
            turn_number=turn_number,
            response_type=response_type,
            response_text=response_text,
            selected_option_id=selected_option_id,
            response_time_seconds=response_time_seconds,
            metadata=metadata or {}
        )

        self.current_session.add_response(response)

        # Auto-save after each response
        self.save_session()

        return response

    def save_session(self, session: Optional[EvaluationSession] = None):
        """
        Save evaluation session to disk.

        Args:
            session: Session to save (defaults to current session)
        """
        session = session or self.current_session
        if not session:
            raise ValueError("No session to save")

        filename = f"session_{session.session_id}.json"
        filepath = self.output_dir / filename

        with open(filepath, 'w') as f:
            json.dump(session.to_dict(), f, indent=2)

    def load_session(self, session_id: str) -> EvaluationSession:
        """
        Load an evaluation session from disk.

        Args:
            session_id: Session ID to load

        Returns:
            Loaded EvaluationSession
        """
        filename = f"session_{session_id}.json"
        filepath = self.output_dir / filename

        if not filepath.exists():
            raise FileNotFoundError(f"Session not found: {session_id}")

        with open(filepath) as f:
            data = json.load(f)

        # Reconstruct session from dict
        # (This is simplified - would need proper deserialization)
        session = EvaluationSession(**{k: v for k, v in data.items() if k != 'responses'})
        session.responses = [EvaluatorResponse(**r) for r in data.get('responses', [])]

        return session

    def get_next_turn(self, evaluation_turns: List[EvaluationTurn]) -> Optional[EvaluationTurn]:
        """
        Get the next turn to evaluate based on current session.

        Args:
            evaluation_turns: All evaluation turns

        Returns:
            Next turn to evaluate, or None if complete
        """
        if not self.current_session:
            return evaluation_turns[0] if evaluation_turns else None

        next_turn_num = len(self.current_session.responses) + 1

        if next_turn_num > len(evaluation_turns):
            return None

        return evaluation_turns[next_turn_num - 1]


class EvaluationAnalyzer:
    """Analyze results from multi-turn evaluations."""

    def __init__(self, sessions_dir: Path):
        """
        Initialize the analyzer.

        Args:
            sessions_dir: Directory containing session files
        """
        self.sessions_dir = Path(sessions_dir)

    def load_all_sessions(self) -> List[EvaluationSession]:
        """Load all evaluation sessions."""
        sessions = []

        for filepath in self.sessions_dir.glob("session_*.json"):
            with open(filepath) as f:
                data = json.load(f)

            # Reconstruct session
            session = EvaluationSession(**{k: v for k, v in data.items() if k != 'responses'})
            session.responses = [EvaluatorResponse(**r) for r in data.get('responses', [])]
            sessions.append(session)

        return sessions

    def compare_evaluators(
        self,
        conversation_id: str,
        evaluator_ids: List[str]
    ) -> Dict:
        """
        Compare responses from different evaluators on the same conversation.

        Args:
            conversation_id: Conversation to compare
            evaluator_ids: List of evaluator IDs to compare

        Returns:
            Comparison results
        """
        sessions = self.load_all_sessions()

        # Filter sessions for this conversation and evaluators
        relevant_sessions = [
            s for s in sessions
            if s.conversation_id == conversation_id and s.evaluator_id in evaluator_ids
        ]

        if not relevant_sessions:
            return {'error': 'No matching sessions found'}

        # Compare turn by turn
        comparison = {
            'conversation_id': conversation_id,
            'evaluators': evaluator_ids,
            'turn_comparisons': []
        }

        max_turns = max(len(s.responses) for s in relevant_sessions)

        for turn_num in range(1, max_turns + 1):
            turn_comparison = {
                'turn_number': turn_num,
                'responses': {}
            }

            for session in relevant_sessions:
                if turn_num <= len(session.responses):
                    response = session.responses[turn_num - 1]
                    turn_comparison['responses'][session.evaluator_id] = {
                        'response_type': response.response_type,
                        'response_text': response.response_text,
                        'selected_option_id': response.selected_option_id,
                        'response_time': response.response_time_seconds
                    }

            comparison['turn_comparisons'].append(turn_comparison)

        return comparison

    def analyze_response_patterns(self, evaluator_type: str = None) -> Dict:
        """
        Analyze patterns in evaluator responses.

        Args:
            evaluator_type: Optional filter by evaluator type

        Returns:
            Analysis results
        """
        sessions = self.load_all_sessions()

        if evaluator_type:
            sessions = [s for s in sessions if s.evaluator_type == evaluator_type]

        analysis = {
            'total_sessions': len(sessions),
            'completed_sessions': len([s for s in sessions if s.status == 'completed']),
            'response_type_distribution': {'free_form': 0, 'multiple_choice': 0},
            'avg_response_time': [],
            'completion_rate': 0
        }

        for session in sessions:
            for response in session.responses:
                analysis['response_type_distribution'][response.response_type] += 1

                if response.response_time_seconds:
                    analysis['avg_response_time'].append(response.response_time_seconds)

        if analysis['avg_response_time']:
            analysis['avg_response_time'] = sum(analysis['avg_response_time']) / len(analysis['avg_response_time'])
        else:
            analysis['avg_response_time'] = None

        if analysis['total_sessions'] > 0:
            analysis['completion_rate'] = analysis['completed_sessions'] / analysis['total_sessions']

        return analysis
