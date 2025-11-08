#!/usr/bin/env python3
"""
Process the therapy conversations dataset and convert patient responses to GenAlpha speak.

This script handles the specific format of the Kaggle therapy dataset where conversations
are stored as JSON strings containing human/gpt exchanges.
"""

import pandas as pd
import json
import ast
import argparse
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from genalpha_converter import GenAlphaConverter


def parse_conversation(conversation_str):
    """
    Parse a conversation string into structured data.

    Args:
        conversation_str: String representation of conversation list

    Returns:
        List of dicts with 'from' and 'value' keys
    """
    try:
        # The conversation format has dict items separated by newlines but NO COMMAS
        # We need to add commas between } and \n {
        import re

        # Replace escaped quotes
        cleaned = conversation_str.replace("\\'", "'")

        # Add commas between list items: }\n { becomes },\n {
        cleaned = re.sub(r'\}\s*\n\s*\{', '},\n{', cleaned)

        conversation = eval(cleaned)
        return conversation
    except Exception as e:
        print(f"Warning: Could not parse conversation: {str(e)[:100]}")
        return []


def extract_patient_responses(conversation):
    """Extract all patient (human) responses from a conversation."""
    return [turn['value'] for turn in conversation if turn['from'] == 'human']


def extract_therapist_responses(conversation):
    """Extract all therapist (gpt) responses from a conversation."""
    return [turn['value'] for turn in conversation if turn['from'] == 'gpt']


def convert_conversation_to_genalpha(conversation_str, converter):
    """
    Convert patient responses in a conversation to GenAlpha speak.

    Args:
        conversation_str: String representation of conversation
        converter: GenAlphaConverter instance

    Returns:
        tuple: (original_conversation_list, genalpha_conversation_list)
    """
    conversation = parse_conversation(conversation_str)

    # Create a copy for GenAlpha version
    genalpha_conversation = []

    for turn in conversation:
        turn_copy = turn.copy()
        if turn['from'] == 'human':
            # Convert patient response to GenAlpha
            turn_copy['value'] = converter.convert_text(turn['value'], context="patient")
        genalpha_conversation.append(turn_copy)

    return conversation, genalpha_conversation


def process_dataset(input_path, output_path, intensity=0.7, sample_size=None):
    """
    Process the dataset and create GenAlpha versions.

    Args:
        input_path: Path to input CSV
        output_path: Path to output CSV
        intensity: Conversion intensity (0.0-1.0)
        sample_size: Optional limit on number of conversations to process
    """
    print(f"Loading dataset from {input_path}...")
    df = pd.read_csv(input_path)

    if sample_size:
        df = df.head(sample_size)
        print(f"Limited to {sample_size} conversations")

    print(f"Processing {len(df)} conversations...")

    # Initialize converter
    converter = GenAlphaConverter(intensity=intensity, use_llm=False)

    # Process each conversation
    results = []
    for idx, row in df.iterrows():
        if idx % 10 == 0:
            print(f"Processing conversation {idx + 1}/{len(df)}...")

        conversation_str = row['conversations']
        conv_original, conv_genalpha = convert_conversation_to_genalpha(conversation_str, converter)

        # Extract first patient and therapist responses for quick reference
        patient_responses_orig = extract_patient_responses(conv_original)
        patient_responses_ga = extract_patient_responses(conv_genalpha)
        therapist_responses = extract_therapist_responses(conv_original)

        results.append({
            'id': row['id'],
            'conversation_original': str(conv_original),
            'conversation_genalpha': str(conv_genalpha),
            'first_patient_original': patient_responses_orig[0] if patient_responses_orig else '',
            'first_patient_genalpha': patient_responses_ga[0] if patient_responses_ga else '',
            'first_therapist': therapist_responses[0] if therapist_responses else '',
            'num_turns': len(conv_original),
            'num_patient_turns': len(patient_responses_orig),
        })

    # Create output dataframe
    result_df = pd.DataFrame(results)

    # Save
    output_path.parent.mkdir(parents=True, exist_ok=True)
    result_df.to_csv(output_path, index=False)
    print(f"\nSaved processed dataset to {output_path}")

    # Show examples
    print("\n" + "="*80)
    print("EXAMPLE CONVERSIONS")
    print("="*80)

    for i in range(min(3, len(result_df))):
        print(f"\n--- Example {i + 1} ---")
        print(f"Original: {result_df['first_patient_original'].iloc[i][:150]}...")
        print(f"GenAlpha: {result_df['first_patient_genalpha'].iloc[i][:150]}...")

    print("\n" + "="*80)
    print(f"Total conversations processed: {len(result_df)}")
    print(f"Average turns per conversation: {result_df['num_turns'].mean():.1f}")
    print(f"Average patient turns: {result_df['num_patient_turns'].mean():.1f}")
    print("="*80)


def main():
    parser = argparse.ArgumentParser(
        description="Process therapy dataset and convert to GenAlpha speak"
    )
    parser.add_argument("--input", type=Path,
                       default=Path("results/evaluation_subset.csv"),
                       help="Input CSV file")
    parser.add_argument("--output", type=Path,
                       default=Path("results/evaluation_subset_genalpha.csv"),
                       help="Output CSV file")
    parser.add_argument("--intensity", type=float, default=0.7,
                       help="Conversion intensity (0.0-1.0)")
    parser.add_argument("--sample-size", type=int, default=None,
                       help="Limit number of conversations to process")

    args = parser.parse_args()

    process_dataset(
        input_path=args.input,
        output_path=args.output,
        intensity=args.intensity,
        sample_size=args.sample_size
    )


if __name__ == "__main__":
    main()
