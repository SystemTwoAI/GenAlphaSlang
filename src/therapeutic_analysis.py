"""
Therapeutic conversation analysis utilities

Author: Manisha Mehta (manisha.mehta@systemtwoai.com)
Date: November 2025
"""

import re
from typing import List, Dict, Tuple
from collections import defaultdict


class TherapeuticAnalyzer:
    """Analyze therapeutic quality of conversations."""

    # Therapeutic technique markers
    EMPATHY_PHRASES = [
        'i understand', 'i hear', 'that sounds', 'it seems', 'it must',
        'i can imagine', 'i appreciate', 'that makes sense', 'i can see'
    ]

    REFLECTION_PHRASES = [
        'you mentioned', 'you said', 'you feel', 'you\'re feeling',
        'sounds like you', 'it seems like you', 'you\'re experiencing',
        'from what you\'re saying'
    ]

    VALIDATION_PHRASES = [
        'that\'s valid', 'that makes sense', 'it\'s understandable',
        'it\'s normal', 'that\'s a common', 'you\'re not alone',
        'it\'s okay to', 'that\'s completely'
    ]

    REFRAME_PHRASES = [
        'another way', 'from a different', 'perspective',
        'what if', 'have you considered', 'could it be',
        'it\'s possible that', 'perhaps'
    ]

    SUMMARY_PHRASES = [
        'so what i\'m hearing', 'let me make sure', 'to summarize',
        'it sounds like overall', 'from what you\'ve shared',
        'if i understand correctly'
    ]

    OPEN_QUESTION_PATTERNS = [
        r'\bhow\b.*\?',
        r'\bwhat\b.*\?',
        r'\bwhy\b.*\?',
        r'\btell me\b.*\?',
        r'\bdescribe\b.*\?',
        r'\bexplain\b.*\?',
        r'\bcan you (tell|share|describe)\b.*\?'
    ]

    def __init__(self):
        """Initialize the analyzer."""
        self.compiled_patterns = [
            re.compile(pattern, re.IGNORECASE)
            for pattern in self.OPEN_QUESTION_PATTERNS
        ]

    def analyze_empathy(self, text: str) -> bool:
        """
        Detect empathy markers in text.

        Args:
            text: Text to analyze

        Returns:
            True if empathy markers found
        """
        text_lower = text.lower()
        return any(phrase in text_lower for phrase in self.EMPATHY_PHRASES)

    def analyze_reflection(self, text: str) -> bool:
        """
        Detect reflection statements.

        Args:
            text: Text to analyze

        Returns:
            True if reflection markers found
        """
        text_lower = text.lower()
        return any(phrase in text_lower for phrase in self.REFLECTION_PHRASES)

    def analyze_validation(self, text: str) -> bool:
        """
        Detect validation statements.

        Args:
            text: Text to analyze

        Returns:
            True if validation markers found
        """
        text_lower = text.lower()
        return any(phrase in text_lower for phrase in self.VALIDATION_PHRASES)

    def analyze_reframe(self, text: str) -> bool:
        """
        Detect reframing attempts.

        Args:
            text: Text to analyze

        Returns:
            True if reframe markers found
        """
        text_lower = text.lower()
        return any(phrase in text_lower for phrase in self.REFRAME_PHRASES)

    def analyze_summary(self, text: str) -> bool:
        """
        Detect summarization statements.

        Args:
            text: Text to analyze

        Returns:
            True if summary markers found
        """
        text_lower = text.lower()
        return any(phrase in text_lower for phrase in self.SUMMARY_PHRASES)

    def count_questions(self, text: str) -> Dict[str, int]:
        """
        Count open and closed questions.

        Args:
            text: Text to analyze

        Returns:
            Dict with 'total', 'open', 'closed' question counts
        """
        total_questions = text.count('?')

        # Count open questions using patterns
        open_questions = sum(
            1 for pattern in self.compiled_patterns
            if pattern.search(text)
        )

        # Make sure we don't overcount
        open_questions = min(open_questions, total_questions)

        return {
            'total': total_questions,
            'open': open_questions,
            'closed': total_questions - open_questions
        }

    def analyze_turn(self, text: str) -> Dict[str, any]:
        """
        Analyze a single therapist turn for all therapeutic techniques.

        Args:
            text: Therapist message text

        Returns:
            Dict with boolean flags for each technique
        """
        question_counts = self.count_questions(text)

        return {
            'has_empathy': self.analyze_empathy(text),
            'has_reflection': self.analyze_reflection(text),
            'has_validation': self.analyze_validation(text),
            'has_reframe': self.analyze_reframe(text),
            'has_summary': self.analyze_summary(text),
            'has_questions': question_counts['total'] > 0,
            'has_open_questions': question_counts['open'] > 0,
            'question_counts': question_counts,
            'word_count': len(text.split())
        }

    def analyze_conversation(self, conversation: List[Dict]) -> Dict:
        """
        Analyze full conversation for therapeutic quality.

        Args:
            conversation: List of conversation turns

        Returns:
            Dict with comprehensive therapeutic quality metrics
        """
        # Extract therapist messages
        therapist_msgs = [
            msg['value'] for msg in conversation
            if msg.get('from') == 'gpt'
        ]

        if not therapist_msgs:
            return self._empty_metrics()

        # Analyze each turn
        turn_analyses = [self.analyze_turn(msg) for msg in therapist_msgs]

        # Aggregate metrics
        metrics = {
            'total_therapist_turns': len(therapist_msgs),

            # Technique counts
            'empathy_count': sum(t['has_empathy'] for t in turn_analyses),
            'reflection_count': sum(t['has_reflection'] for t in turn_analyses),
            'validation_count': sum(t['has_validation'] for t in turn_analyses),
            'reframe_count': sum(t['has_reframe'] for t in turn_analyses),
            'summary_count': sum(t['has_summary'] for t in turn_analyses),

            # Question counts
            'total_questions': sum(t['question_counts']['total'] for t in turn_analyses),
            'open_questions': sum(t['question_counts']['open'] for t in turn_analyses),
            'closed_questions': sum(t['question_counts']['closed'] for t in turn_analyses),

            # Word statistics
            'total_words': sum(t['word_count'] for t in turn_analyses),
            'avg_words_per_turn': sum(t['word_count'] for t in turn_analyses) / len(therapist_msgs)
        }

        # Calculate rates (per turn)
        total_turns = metrics['total_therapist_turns']
        metrics['empathy_rate'] = metrics['empathy_count'] / total_turns
        metrics['reflection_rate'] = metrics['reflection_count'] / total_turns
        metrics['validation_rate'] = metrics['validation_count'] / total_turns
        metrics['reframe_rate'] = metrics['reframe_count'] / total_turns
        metrics['summary_rate'] = metrics['summary_count'] / total_turns
        metrics['question_rate'] = metrics['total_questions'] / total_turns
        metrics['open_question_rate'] = metrics['open_questions'] / total_turns

        return metrics

    def _empty_metrics(self) -> Dict:
        """Return empty metrics dict for conversations with no therapist turns."""
        return {
            'total_therapist_turns': 0,
            'empathy_count': 0,
            'reflection_count': 0,
            'validation_count': 0,
            'reframe_count': 0,
            'summary_count': 0,
            'total_questions': 0,
            'open_questions': 0,
            'closed_questions': 0,
            'total_words': 0,
            'avg_words_per_turn': 0,
            'empathy_rate': 0,
            'reflection_rate': 0,
            'validation_rate': 0,
            'reframe_rate': 0,
            'summary_rate': 0,
            'question_rate': 0,
            'open_question_rate': 0
        }

    def assess_quality(self, metrics: Dict) -> Tuple[str, List[str]]:
        """
        Assess overall therapeutic quality based on metrics.

        Args:
            metrics: Output from analyze_conversation()

        Returns:
            Tuple of (quality_rating, list_of_strengths_and_weaknesses)
        """
        score = 0
        max_score = 5
        feedback = []

        # Criterion 1: Empathy
        if metrics['empathy_rate'] > 0.5:
            score += 1
            feedback.append("✓ High empathy presence")
        elif metrics['empathy_rate'] > 0.3:
            feedback.append("~ Moderate empathy")
        else:
            feedback.append("✗ Low empathy (may seem robotic)")

        # Criterion 2: Questions
        if metrics['question_rate'] > 0.4:
            score += 1
            feedback.append("✓ Good question usage")
        elif metrics['question_rate'] > 0.2:
            feedback.append("~ Moderate question usage")
        else:
            feedback.append("✗ Low question usage")

        # Criterion 3: Open questions
        if metrics['open_question_rate'] > 0.3:
            score += 1
            feedback.append("✓ Good use of open questions")
        else:
            feedback.append("~ Could use more open questions")

        # Criterion 4: Reflection
        if metrics['reflection_rate'] > 0.2:
            score += 1
            feedback.append("✓ Good use of reflection")
        else:
            feedback.append("~ Limited reflection")

        # Criterion 5: Validation
        if metrics['validation_rate'] > 0.1:
            score += 1
            feedback.append("✓ Validates patient feelings")
        else:
            feedback.append("~ Limited validation")

        # Overall rating
        if score >= 4:
            rating = "HIGH"
        elif score >= 3:
            rating = "MODERATE"
        else:
            rating = "LOW"

        return rating, feedback
