"""
Streamlit App for GenAlpha Therapy Conversation Explorer

Interactive UI for:
- Browsing therapy conversations
- Converting to GenAlpha speak
- Comparing original vs GenAlpha versions
- Exploring benchmarks
"""

import streamlit as st
import requests
import pandas as pd
from pathlib import Path
import sys
import json

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from genalpha_converter import GenAlphaConverter

# Page config
st.set_page_config(
    page_title="GenAlpha Therapy Explorer",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# API configuration
USE_API = False  # Set to True if FastAPI backend is running
API_URL = "http://localhost:8000"

# Initialize session state
if 'benchmark' not in st.session_state:
    st.session_state.benchmark = 'mini'
if 'conversation_idx' not in st.session_state:
    st.session_state.conversation_idx = 0
if 'intensity' not in st.session_state:
    st.session_state.intensity = 0.7
if 'converter' not in st.session_state:
    st.session_state.converter = GenAlphaConverter(intensity=0.7, use_llm=False)


def parse_conversation(conversation_str):
    """Parse conversation string into structured data."""
    import re
    try:
        cleaned = conversation_str.replace("\\'", "'")
        cleaned = re.sub(r'\}\s*\n\s*\{', '},\n{', cleaned)
        conversation = eval(cleaned)
        return conversation
    except Exception as e:
        st.error(f"Error parsing conversation: {e}")
        return []


def load_benchmark_local(benchmark_name):
    """Load benchmark data locally."""
    results_dir = Path(__file__).parent.parent / "results"

    file_mapping = {
        "mini": "benchmark_mini_50.csv",
        "standard": "benchmark_standard_200.csv",
        "stratified": "benchmark_stratified_300.csv",
        "comprehensive": "benchmark_comprehensive_500.csv",
        "evaluation_subset": "evaluation_subset.csv",
        "evaluation_subset_genalpha": "evaluation_subset_genalpha.csv",
    }

    file_path = results_dir / file_mapping.get(benchmark_name, "benchmark_mini_50.csv")

    if file_path.exists():
        return pd.read_csv(file_path)
    else:
        st.error(f"Benchmark file not found: {file_path}")
        return None


def display_conversation(conv_data, show_genalpha=False, intensity=0.7):
    """Display a conversation with formatting."""
    if not conv_data:
        st.warning("No conversation data")
        return

    # Update converter intensity if needed
    if intensity != st.session_state.converter.intensity:
        st.session_state.converter = GenAlphaConverter(intensity=intensity, use_llm=False)

    for i, turn in enumerate(conv_data):
        speaker = turn.get('from', 'unknown')
        message = turn.get('value', '')

        if speaker == 'human':
            # Patient message
            with st.container():
                col1, col2 = st.columns([1, 1])

                with col1:
                    st.markdown("**🧑 Patient (Original):**")
                    st.info(message)

                if show_genalpha:
                    with col2:
                        st.markdown("**🧑 Patient (GenAlpha):**")
                        genalpha_message = st.session_state.converter.convert_text(message, context="patient")
                        st.success(genalpha_message)

        else:
            # Therapist message
            st.markdown("**👨‍⚕️ Therapist:**")
            st.warning(message)

        st.divider()


def main():
    st.title("💬 GenAlpha Therapy Conversation Explorer")

    st.markdown("""
    Explore therapy conversations and see how they translate to Gen Alpha speaking style.
    Gen Alpha (born ~2010+) uses modern slang and informal communication patterns.
    """)

    # Sidebar
    with st.sidebar:
        st.header("⚙️ Settings")

        # Benchmark selection
        benchmark_options = {
            "mini": "Mini (50 convos)",
            "standard": "Standard (200 convos)",
            "stratified": "Stratified (300 convos)",
            "comprehensive": "Comprehensive (500 convos)",
            "evaluation_subset": "Evaluation Subset (100 convos)",
            "evaluation_subset_genalpha": "GenAlpha Subset (100 convos)",
        }

        st.session_state.benchmark = st.selectbox(
            "Select Benchmark",
            options=list(benchmark_options.keys()),
            format_func=lambda x: benchmark_options[x],
            index=0
        )

        # Load benchmark
        df = load_benchmark_local(st.session_state.benchmark)

        if df is not None:
            st.success(f"✅ Loaded {len(df)} conversations")

            # Conversation navigation
            st.session_state.conversation_idx = st.number_input(
                "Conversation Index",
                min_value=0,
                max_value=len(df) - 1,
                value=st.session_state.conversation_idx,
                step=1
            )

            # Intensity slider
            st.session_state.intensity = st.slider(
                "GenAlpha Intensity",
                min_value=0.0,
                max_value=1.0,
                value=st.session_state.intensity,
                step=0.1,
                help="How much to transform to GenAlpha speak (0=minimal, 1=maximum)"
            )

            # Info
            st.divider()
            st.subheader("📊 Benchmark Info")
            st.metric("Total Conversations", len(df))
            st.metric("Current Index", st.session_state.conversation_idx)

    # Main content
    if df is None:
        st.error("❌ Could not load benchmark data")
        return

    # Tabs
    tab1, tab2, tab3, tab4 = st.tabs(["💬 Conversation", "📊 Statistics", "🔧 Custom Conversion", "📚 Documentation"])

    with tab1:
        st.header(f"Conversation {st.session_state.conversation_idx}")

        row = df.iloc[st.session_state.conversation_idx]

        # Show conversation ID
        if 'id' in row:
            st.caption(f"ID: {row['id']}")

        # Navigation buttons
        col1, col2, col3 = st.columns([1, 1, 1])
        with col1:
            if st.button("⬅️ Previous", use_container_width=True):
                st.session_state.conversation_idx = max(0, st.session_state.conversation_idx - 1)
                st.rerun()
        with col2:
            st.write("")  # Spacer
        with col3:
            if st.button("Next ➡️", use_container_width=True):
                st.session_state.conversation_idx = min(len(df) - 1, st.session_state.conversation_idx + 1)
                st.rerun()

        # Show GenAlpha toggle
        show_genalpha = st.checkbox("Show GenAlpha Translation", value=True)

        st.divider()

        # Parse and display conversation
        if 'conversations' in row:
            conv = parse_conversation(row['conversations'])
            if conv:
                display_conversation(conv, show_genalpha, st.session_state.intensity)
            else:
                st.error("Could not parse conversation")

        elif 'conversation_original' in row:
            # Already has both versions
            st.subheader("Original Conversation")
            conv_orig = parse_conversation(row['conversation_original'])
            if conv_orig:
                display_conversation(conv_orig, False)

            st.divider()
            st.subheader("GenAlpha Conversation")
            conv_ga = parse_conversation(row['conversation_genalpha'])
            if conv_ga:
                for turn in conv_ga:
                    speaker = turn.get('from', 'unknown')
                    message = turn.get('value', '')
                    if speaker == 'human':
                        st.markdown("**🧑 Patient (GenAlpha):**")
                        st.success(message)
                    else:
                        st.markdown("**👨‍⚕️ Therapist:**")
                        st.warning(message)
                    st.divider()

        else:
            st.info("Raw data view:")
            st.json(row.to_dict())

    with tab2:
        st.header("📊 Benchmark Statistics")

        if 'conversations' in df.columns:
            # Calculate stats
            lengths = []
            patient_counts = []
            therapist_counts = []

            with st.spinner("Analyzing conversations..."):
                for idx, row in df.iterrows():
                    conv = parse_conversation(row['conversations'])
                    if conv:
                        lengths.append(len(conv))
                        patient_counts.append(sum(1 for t in conv if t['from'] == 'human'))
                        therapist_counts.append(sum(1 for t in conv if t['from'] == 'gpt'))

            if lengths:
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Avg Turns", f"{sum(lengths) / len(lengths):.1f}")
                with col2:
                    st.metric("Min Turns", min(lengths))
                with col3:
                    st.metric("Max Turns", max(lengths))

                # Distribution chart
                st.subheader("Turn Distribution")
                import numpy as np
                chart_data = pd.DataFrame({
                    'Turns': lengths
                })
                st.bar_chart(chart_data['Turns'].value_counts().sort_index())

        else:
            st.info("Statistics not available for this benchmark format")

    with tab3:
        st.header("🔧 Custom Text Conversion")

        st.markdown("""
        Test the GenAlpha converter on your own text. Enter any patient message
        and see how it translates to Gen Alpha speaking style.
        """)

        # Text input
        user_text = st.text_area(
            "Enter patient message:",
            value="I've been feeling really anxious about my exams. I can't sleep and I'm worried I'll fail.",
            height=100
        )

        # Intensity for custom
        custom_intensity = st.slider(
            "Conversion Intensity",
            min_value=0.0,
            max_value=1.0,
            value=0.7,
            step=0.1,
            key="custom_intensity"
        )

        if st.button("Convert to GenAlpha", type="primary"):
            if user_text:
                converter = GenAlphaConverter(intensity=custom_intensity, use_llm=False)
                converted = converter.convert_text(user_text, context="patient")

                col1, col2 = st.columns(2)
                with col1:
                    st.subheader("Original")
                    st.info(user_text)
                with col2:
                    st.subheader("GenAlpha")
                    st.success(converted)

                # Show transformations
                st.divider()
                st.subheader("What Changed?")
                if user_text != converted:
                    st.markdown(f"""
                    - **Original length**: {len(user_text)} chars
                    - **GenAlpha length**: {len(converted)} chars
                    - **Intensity**: {custom_intensity}
                    """)
                else:
                    st.info("No changes made at this intensity level")
            else:
                st.warning("Please enter some text to convert")

    with tab4:
        st.header("📚 Documentation")

        st.markdown("""
        ## About GenAlpha Language

        Gen Alpha (born ~2010 onwards) has distinctive communication patterns:

        ### Common Transformations

        | Standard | GenAlpha |
        |----------|----------|
        | "really", "very" | fr (for real), lowkey, highkey |
        | "I agree" | no cap, facts, fr fr |
        | "I don't know" | idk, ion know |
        | "to be honest" | tbh, ngl (not gonna lie) |
        | "cool", "great" | fire, bussin, slaps |
        | "anxious", "worried" | lowkey stressing, tweaking |
        | "sad", "depressed" | in my feels, down bad |

        ### Characteristics
        - **Slang vocabulary**: fr, no cap, bussin, mid, vibing
        - **Abbreviations**: ngl, tbh, idk, idc, ong
        - **Intensifiers**: lowkey, highkey, deadass
        - **Less formal grammar**: Casual structure
        - **Internet influence**: Social media expressions

        ### Using the Explorer

        1. **Select a benchmark** in the sidebar
        2. **Navigate conversations** with the index selector or buttons
        3. **Adjust intensity** to control how much transformation occurs
        4. **Toggle GenAlpha view** to compare original and converted versions
        5. **Try custom text** in the Custom Conversion tab

        ### Benchmarks

        - **Mini (50)**: Quick testing
        - **Standard (200)**: Regular evaluation
        - **Stratified (300)**: Balanced by complexity
        - **Comprehensive (500)**: Thorough analysis
        """)

        st.divider()

        st.markdown("""
        ### Project Links

        - [GitHub Repository](https://github.com/SystemTwoAI/GenAlphaSlang)
        - [Documentation](../docs/)
        - [Benchmark Guide](../docs/BENCHMARK_GUIDE.md)

        ### Research Questions

        1. Do therapy models maintain empathy with GenAlpha slang?
        2. Does informal language affect understanding?
        3. Do models adapt their communication style?
        4. Is therapeutic quality maintained?
        """)


if __name__ == "__main__":
    main()
