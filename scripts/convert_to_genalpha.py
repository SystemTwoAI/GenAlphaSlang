#!/usr/bin/env python3
"""
Convert therapy conversation dataset to GenAlpha speak.

This script takes the evaluation subset and creates GenAlpha versions
of the patient responses.
"""

import pandas as pd
import argparse
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from genalpha_converter import GenAlphaConverter, convert_conversation


def identify_columns(df: pd.DataFrame) -> tuple:
    """
    Identify patient and therapist columns in the dataset.

    Returns:
        (patient_col, therapist_col)
    """
    columns_lower = {col.lower(): col for col in df.columns}

    # Common patterns for patient/therapist columns
    patient_patterns = ['patient', 'client', 'user', 'person']
    therapist_patterns = ['therapist', 'counselor', 'counsellor', 'therapist', 'professional']

    patient_col = None
    therapist_col = None

    # Find patient column
    for pattern in patient_patterns:
        for col_lower, col_actual in columns_lower.items():
            if pattern in col_lower:
                patient_col = col_actual
                break
        if patient_col:
            break

    # Find therapist column
    for pattern in therapist_patterns:
        for col_lower, col_actual in columns_lower.items():
            if pattern in col_lower:
                therapist_col = col_actual
                break
        if therapist_col:
            break

    if not patient_col:
        print("Available columns:", df.columns.tolist())
        raise ValueError("Could not identify patient column. Please specify manually.")

    print(f"Identified columns - Patient: {patient_col}, Therapist: {therapist_col}")
    return patient_col, therapist_col


def convert_dataset(
    df: pd.DataFrame,
    patient_col: str,
    therapist_col: str = None,
    intensity: float = 0.7,
    use_llm: bool = False
) -> pd.DataFrame:
    """
    Convert dataset patient responses to GenAlpha speak.

    Args:
        df: DataFrame with conversations
        patient_col: Column name for patient responses
        therapist_col: Column name for therapist responses (optional)
        intensity: Conversion intensity (0.0-1.0)
        use_llm: Whether to use LLM for conversion

    Returns:
        DataFrame with original and GenAlpha versions
    """
    converter = GenAlphaConverter(intensity=intensity, use_llm=use_llm)

    result_df = df.copy()

    # Store original
    result_df[f'{patient_col}_original'] = result_df[patient_col]

    # Convert to GenAlpha
    print(f"Converting {len(df)} patient responses to GenAlpha speak...")
    result_df[f'{patient_col}_genalpha'] = result_df[patient_col].apply(
        lambda x: converter.convert_text(str(x), context="patient")
    )

    print("Conversion complete!")

    # Show some examples
    print("\nExample conversions:")
    for idx in range(min(3, len(result_df))):
        print(f"\n--- Example {idx + 1} ---")
        print(f"Original: {result_df[f'{patient_col}_original'].iloc[idx]}")
        print(f"GenAlpha: {result_df[f'{patient_col}_genalpha'].iloc[idx]}")

    return result_df


def main():
    parser = argparse.ArgumentParser(description="Convert therapy conversations to GenAlpha speak")
    parser.add_argument("--input", type=Path, required=True,
                       help="Input CSV file (evaluation subset)")
    parser.add_argument("--output", type=Path, required=True,
                       help="Output CSV file with GenAlpha conversions")
    parser.add_argument("--patient-col", type=str, default=None,
                       help="Column name for patient responses (auto-detected if not specified)")
    parser.add_argument("--therapist-col", type=str, default=None,
                       help="Column name for therapist responses (auto-detected if not specified)")
    parser.add_argument("--intensity", type=float, default=0.7,
                       help="Conversion intensity 0.0-1.0 (default: 0.7)")
    parser.add_argument("--use-llm", action="store_true",
                       help="Use LLM for conversion (requires API setup)")

    args = parser.parse_args()

    # Load dataset
    print(f"Loading dataset from {args.input}...")
    df = pd.read_csv(args.input)
    print(f"Loaded {len(df)} conversations")

    # Identify columns
    if args.patient_col:
        patient_col = args.patient_col
        therapist_col = args.therapist_col
    else:
        patient_col, therapist_col = identify_columns(df)

    # Convert
    result_df = convert_dataset(
        df,
        patient_col=patient_col,
        therapist_col=therapist_col,
        intensity=args.intensity,
        use_llm=args.use_llm
    )

    # Save
    args.output.parent.mkdir(parents=True, exist_ok=True)
    result_df.to_csv(args.output, index=False)
    print(f"\nSaved converted dataset to {args.output}")


if __name__ == "__main__":
    main()
