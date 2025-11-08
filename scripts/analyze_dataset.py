#!/usr/bin/env python3
"""
Analyze the therapy conversations dataset and create a representative evaluation subset.

This script:
1. Loads the synthetic therapy conversations dataset
2. Analyzes conversation characteristics (length, topics, sentiment, etc.)
3. Creates a stratified representative subset for evaluation
"""

import pandas as pd
import argparse
from pathlib import Path
import json


def load_dataset(data_path: Path) -> pd.DataFrame:
    """Load the therapy conversations dataset."""
    # Support both CSV and extracted CSV from zip
    csv_files = list(data_path.glob("*.csv"))

    if not csv_files:
        raise FileNotFoundError(f"No CSV files found in {data_path}")

    # Load the first CSV file (or combine if multiple)
    df = pd.read_csv(csv_files[0])

    print(f"Loaded dataset with {len(df)} rows and {len(df.columns)} columns")
    print(f"Columns: {df.columns.tolist()}")

    return df


def analyze_conversations(df: pd.DataFrame) -> dict:
    """Analyze conversation characteristics."""
    stats = {
        "total_conversations": len(df),
        "columns": df.columns.tolist(),
        "sample_data": df.head(3).to_dict('records'),
    }

    # Try to identify conversation-related columns
    for col in df.columns:
        if 'length' in col.lower() or 'len' in col.lower():
            stats[f"{col}_stats"] = df[col].describe().to_dict()

        # Check for text columns
        if df[col].dtype == 'object':
            stats[f"{col}_unique"] = df[col].nunique()
            stats[f"{col}_sample"] = df[col].head(3).tolist()

    return stats


def create_representative_subset(
    df: pd.DataFrame,
    n_samples: int = 100,
    stratify_column: str = None,
    random_state: int = 42
) -> pd.DataFrame:
    """
    Create a representative subset of the dataset.

    Args:
        df: Full dataset
        n_samples: Number of samples to include in subset
        stratify_column: Column to stratify by (e.g., topic, length category)
        random_state: Random seed for reproducibility
    """
    if stratify_column and stratify_column in df.columns:
        # Stratified sampling
        subset = df.groupby(stratify_column, group_keys=False).apply(
            lambda x: x.sample(min(len(x), max(1, int(n_samples * len(x) / len(df)))),
                              random_state=random_state)
        )
    else:
        # Simple random sampling
        subset = df.sample(n=min(n_samples, len(df)), random_state=random_state)

    print(f"Created subset with {len(subset)} samples")
    return subset


def main():
    parser = argparse.ArgumentParser(description="Analyze therapy dataset and create evaluation subset")
    parser.add_argument("--data-dir", type=Path, default=Path("data"),
                       help="Directory containing the dataset")
    parser.add_argument("--output-dir", type=Path, default=Path("results"),
                       help="Directory to save analysis results")
    parser.add_argument("--subset-size", type=int, default=100,
                       help="Size of evaluation subset")
    parser.add_argument("--stratify-by", type=str, default=None,
                       help="Column to stratify subset by")

    args = parser.parse_args()

    # Create output directory
    args.output_dir.mkdir(parents=True, exist_ok=True)

    # Load dataset
    print("Loading dataset...")
    df = load_dataset(args.data_dir)

    # Analyze
    print("\nAnalyzing dataset...")
    stats = analyze_conversations(df)

    # Save analysis
    stats_file = args.output_dir / "dataset_analysis.json"
    with open(stats_file, 'w') as f:
        json.dump(stats, f, indent=2, default=str)
    print(f"Saved analysis to {stats_file}")

    # Create representative subset
    print("\nCreating representative subset...")
    subset = create_representative_subset(
        df,
        n_samples=args.subset_size,
        stratify_column=args.stratify_by
    )

    # Save subset
    subset_file = args.output_dir / "evaluation_subset.csv"
    subset.to_csv(subset_file, index=False)
    print(f"Saved evaluation subset to {subset_file}")

    print("\nDone!")


if __name__ == "__main__":
    main()
