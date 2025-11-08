"""
Streamlit UI for multi-turn therapy conversation evaluation.

Allows evaluators to respond turn-by-turn with either free-form or multiple-choice.

Author: Manisha Mehta (manisha.mehta@systemtwoai.com)
Date: November 2025
"""

import streamlit as st
import pandas as pd
import sys
from pathlib import Path
import time

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from multi_turn_evaluator import (
    MultiTurnEvaluator,
    EvaluationAnalyzer,
    EvaluationTurn,
    Turn
)
from utils import parse_conversation, load_benchmark


def initialize_session_state():
    """Initialize Streamlit session state."""
    if 'evaluator' not in st.session_state:
        output_dir = Path(__file__).parent.parent / 'results' / 'evaluation_sessions'
        st.session_state.evaluator = MultiTurnEvaluator(output_dir)

    if 'current_conversation' not in st.session_state:
        st.session_state.current_conversation = None

    if 'evaluation_turns' not in st.session_state:
        st.session_state.evaluation_turns = []

    if 'current_turn_index' not in st.session_state:
        st.session_state.current_turn_index = 0

    if 'evaluator_id' not in st.session_state:
        st.session_state.evaluator_id = None

    if 'start_time' not in st.session_state:
        st.session_state.start_time = None


def display_conversation_history(history: list):
    """Display conversation history."""
    st.markdown("### Conversation So Far")

    for turn in history:
        if turn.speaker == 'patient':
            st.markdown(f"**Patient:** {turn.text}")
        else:
            st.markdown(f"**Therapist:** {turn.text}")

    st.markdown("---")


def display_evaluation_turn(eval_turn: EvaluationTurn, turn_index: int):
    """Display a single evaluation turn."""
    st.markdown(f"### Turn {eval_turn.turn_number}")

    # Show conversation history
    if eval_turn.conversation_history:
        with st.expander("View Conversation History", expanded=False):
            for turn in eval_turn.conversation_history:
                role = "🧑 Patient" if turn.speaker == 'patient' else "💬 Therapist"
                st.markdown(f"**{role}:** {turn.text}")

    # Show current patient message
    st.markdown("#### Patient Says:")
    if eval_turn.is_genalpha:
        st.info(f"🗣️ (GenAlpha) {eval_turn.patient_message}")
    else:
        st.info(f"🗣️ {eval_turn.patient_message}")

    st.markdown("#### Your Response:")

    # Response mode selection
    response_mode = st.radio(
        "Response Mode",
        ["Write Your Own Response", "Select from Options"],
        key=f"mode_{turn_index}",
        horizontal=True
    )

    response_text = None
    response_type = None
    selected_option_id = None

    if response_mode == "Write Your Own Response":
        # Free-form text area
        response_text = st.text_area(
            "Write your therapeutic response:",
            height=150,
            key=f"free_form_{turn_index}",
            placeholder="Type your response as a therapist would..."
        )
        response_type = "free_form"

    else:
        # Multiple choice
        if eval_turn.response_options:
            st.markdown("**Select a response:**")

            for i, option in enumerate(eval_turn.response_options):
                label = option.label if option.label else f"Option {i+1}"

                if st.button(
                    f"**{label}**",
                    key=f"option_btn_{turn_index}_{i}",
                    use_container_width=True
                ):
                    response_text = option.text
                    selected_option_id = option.id
                    response_type = "multiple_choice"

                st.markdown(f"_{option.text[:200]}{'...' if len(option.text) > 200 else ''}_")
                st.markdown("")

        else:
            st.warning("No multiple-choice options available for this turn.")
            response_text = st.text_area(
                "Write your response:",
                height=150,
                key=f"fallback_{turn_index}"
            )
            response_type = "free_form"

    return response_text, response_type, selected_option_id


def evaluation_page():
    """Main evaluation page."""
    st.title("🧠 Therapy Conversation Evaluation")
    st.markdown("Respond to patient messages turn-by-turn as a therapist")

    # Sidebar: Setup
    with st.sidebar:
        st.header("Setup")

        # Evaluator ID
        if not st.session_state.evaluator_id:
            evaluator_id = st.text_input(
                "Your Evaluator ID",
                placeholder="e.g., evaluator_001, GPT-4, Claude",
                help="Unique identifier for this evaluation session"
            )

            evaluator_type = st.selectbox(
                "Evaluator Type",
                ["human", "claude", "gpt4", "gemini", "other"]
            )

            if st.button("Start Evaluation"):
                if evaluator_id:
                    st.session_state.evaluator_id = evaluator_id
                    st.session_state.evaluator_type = evaluator_type
                    st.rerun()
                else:
                    st.error("Please enter an Evaluator ID")

        else:
            st.success(f"Evaluator: {st.session_state.evaluator_id}")
            st.info(f"Type: {st.session_state.evaluator_type}")

            if st.button("Reset"):
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                st.rerun()

        st.markdown("---")

        # Conversation selection
        if st.session_state.evaluator_id and not st.session_state.current_conversation:
            st.header("Select Conversation")

            benchmark = st.selectbox(
                "Benchmark",
                ["benchmark_mini_50.csv", "benchmark_standard_200.csv"]
            )

            df = load_benchmark(benchmark)

            conversation_ids = df['id'].tolist()
            selected_id = st.selectbox("Conversation ID", conversation_ids)

            version = st.radio("Version", ["Original", "GenAlpha"])

            max_turns = st.slider("Number of Turns", 1, 10, 5)

            if st.button("Load Conversation"):
                # Load the conversation
                row = df[df['id'] == selected_id].iloc[0]
                conversation = parse_conversation(row['conversations'])

                # Create evaluation turns
                evaluation_turns = st.session_state.evaluator.create_evaluation_turns(
                    conversation,
                    max_turns=max_turns,
                    generate_options=True,
                    num_options=3
                )

                # Start session
                st.session_state.evaluator.start_session(
                    conversation_id=selected_id,
                    evaluator_id=st.session_state.evaluator_id,
                    evaluator_type=st.session_state.evaluator_type,
                    evaluation_turns=evaluation_turns,
                    is_genalpha=(version == "GenAlpha")
                )

                st.session_state.current_conversation = selected_id
                st.session_state.evaluation_turns = evaluation_turns
                st.session_state.current_turn_index = 0
                st.session_state.start_time = time.time()

                st.rerun()

    # Main content
    if not st.session_state.evaluator_id:
        st.info("👈 Please enter your Evaluator ID in the sidebar to begin")
        return

    if not st.session_state.current_conversation:
        st.info("👈 Please select a conversation from the sidebar")
        return

    # Display progress
    current_session = st.session_state.evaluator.current_session
    if current_session:
        progress = len(current_session.responses) / current_session.max_turns
        st.progress(progress)
        st.markdown(f"**Progress:** Turn {len(current_session.responses) + 1} of {current_session.max_turns}")

    # Check if evaluation is complete
    if st.session_state.current_turn_index >= len(st.session_state.evaluation_turns):
        st.success("🎉 Evaluation Complete!")
        st.balloons()

        st.markdown("### Your Responses")
        if current_session:
            for i, response in enumerate(current_session.responses, 1):
                with st.expander(f"Turn {i} - {response.response_type}"):
                    st.markdown(response.response_text)

        if st.button("Start New Evaluation"):
            st.session_state.current_conversation = None
            st.session_state.evaluation_turns = []
            st.session_state.current_turn_index = 0
            st.rerun()

        return

    # Display current turn
    current_turn = st.session_state.evaluation_turns[st.session_state.current_turn_index]

    response_text, response_type, selected_option_id = display_evaluation_turn(
        current_turn,
        st.session_state.current_turn_index
    )

    # Submit button
    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        if st.button("Submit Response", type="primary", use_container_width=True):
            if not response_text or not response_type:
                st.error("Please provide a response before submitting")
            else:
                # Calculate response time
                response_time = None
                if st.session_state.start_time:
                    response_time = time.time() - st.session_state.start_time

                # Submit the response
                st.session_state.evaluator.submit_response(
                    turn_number=current_turn.turn_number,
                    response_text=response_text,
                    response_type=response_type,
                    selected_option_id=selected_option_id,
                    response_time_seconds=response_time
                )

                # Move to next turn
                st.session_state.current_turn_index += 1
                st.session_state.start_time = time.time()  # Reset timer for next turn

                st.rerun()


def analysis_page():
    """Analysis page for completed evaluations."""
    st.title("📊 Evaluation Analysis")

    output_dir = Path(__file__).parent.parent / 'results' / 'evaluation_sessions'
    analyzer = EvaluationAnalyzer(output_dir)

    # Load all sessions
    sessions = analyzer.load_all_sessions()

    if not sessions:
        st.info("No evaluation sessions found yet.")
        return

    st.markdown(f"**Total Sessions:** {len(sessions)}")

    # Overall statistics
    st.header("Overall Statistics")

    stats = analyzer.analyze_response_patterns()

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Completed Sessions", stats['completed_sessions'])

    with col2:
        st.metric("Completion Rate", f"{stats['completion_rate']:.1%}")

    with col3:
        if stats['avg_response_time']:
            st.metric("Avg Response Time", f"{stats['avg_response_time']:.1f}s")

    # Response type distribution
    st.subheader("Response Type Distribution")
    response_dist = pd.DataFrame([
        {"Type": "Free Form", "Count": stats['response_type_distribution']['free_form']},
        {"Type": "Multiple Choice", "Count": stats['response_type_distribution']['multiple_choice']}
    ])
    st.bar_chart(response_dist.set_index("Type"))

    # Session details
    st.header("Session Details")

    for session in sessions:
        with st.expander(f"Session {session.session_id[:8]}... - {session.evaluator_id}"):
            st.markdown(f"**Conversation:** {session.conversation_id}")
            st.markdown(f"**Evaluator Type:** {session.evaluator_type}")
            st.markdown(f"**Status:** {session.status}")
            st.markdown(f"**Responses:** {len(session.responses)}/{session.max_turns}")

            if session.responses:
                st.markdown("**Responses:**")
                for response in session.responses:
                    st.markdown(f"- Turn {response.turn_number}: {response.response_type}")


def main():
    """Main application."""
    st.set_page_config(
        page_title="Therapy Evaluation Platform",
        page_icon="🧠",
        layout="wide"
    )

    initialize_session_state()

    # Navigation
    page = st.sidebar.radio("Navigation", ["Evaluate", "Analysis"])

    if page == "Evaluate":
        evaluation_page()
    else:
        analysis_page()


if __name__ == '__main__':
    main()
