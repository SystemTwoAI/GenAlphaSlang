#!/usr/bin/env python3
"""
Run evaluation comparing model behavior on original vs GenAlpha conversations.

This script:
1. Loads the converted dataset
2. Generates model responses for both versions
3. Evaluates and compares the responses
4. Produces analysis and visualizations
"""

import pandas as pd
import argparse
from pathlib import Path
import sys
import json

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from evaluator import (
    TherapyEvaluator,
    OpenAIModelInterface,
    AnthropicModelInterface,
    aggregate_results
)


def main():
    parser = argparse.ArgumentParser(
        description="Evaluate model responses to original vs GenAlpha conversations"
    )
    parser.add_argument("--input", type=Path, required=True,
                       help="Input CSV with original and GenAlpha conversations")
    parser.add_argument("--output-dir", type=Path, default=Path("results"),
                       help="Directory to save results")
    parser.add_argument("--model", type=str, default="gpt-4",
                       choices=["gpt-3.5-turbo", "gpt-4", "claude-3-sonnet", "claude-3-opus"],
                       help="Model to evaluate")
    parser.add_argument("--original-col", type=str, required=True,
                       help="Column name for original patient messages")
    parser.add_argument("--genalpha-col", type=str, required=True,
                       help="Column name for GenAlpha patient messages")
    parser.add_argument("--therapist-col", type=str, default=None,
                       help="Column name for ground truth therapist responses")
    parser.add_argument("--api-key", type=str, default=None,
                       help="API key for the model (or set via environment variable)")
    parser.add_argument("--limit", type=int, default=None,
                       help="Limit number of conversations to evaluate (for testing)")

    args = parser.parse_args()

    # Create output directory
    args.output_dir.mkdir(parents=True, exist_ok=True)

    # Load dataset
    print(f"Loading dataset from {args.input}...")
    df = pd.read_csv(args.input)

    if args.limit:
        df = df.head(args.limit)
        print(f"Limited to {args.limit} conversations for testing")

    print(f"Loaded {len(df)} conversations")

    # Initialize model interface
    print(f"Initializing {args.model}...")
    if args.model.startswith("gpt"):
        model_interface = OpenAIModelInterface(model_name=args.model, api_key=args.api_key)
    elif args.model.startswith("claude"):
        model_interface = AnthropicModelInterface(model_name=args.model, api_key=args.api_key)
    else:
        raise ValueError(f"Unknown model: {args.model}")

    # Initialize evaluator
    evaluator = TherapyEvaluator(model_interface)

    # Run evaluation
    print("\nRunning evaluation...")
    print("This will generate model responses and evaluate them...")
    print("(Note: Actual API calls are not implemented in this demo version)\n")

    results_df = evaluator.evaluate_dataset(
        df,
        original_col=args.original_col,
        genalpha_col=args.genalpha_col,
        therapist_col=args.therapist_col
    )

    # Save detailed results
    results_file = args.output_dir / f"evaluation_results_{args.model}.csv"
    results_df.to_csv(results_file, index=False)
    print(f"\nSaved detailed results to {results_file}")

    # Aggregate and save summary
    print("\nGenerating aggregate statistics...")
    summary = aggregate_results(results_df)

    summary_file = args.output_dir / f"evaluation_summary_{args.model}.json"
    with open(summary_file, 'w') as f:
        json.dump(summary, f, indent=2)
    print(f"Saved summary to {summary_file}")

    # Print summary
    print("\n" + "="*60)
    print("EVALUATION SUMMARY")
    print("="*60)
    print(f"\nModel: {args.model}")
    print(f"Sample size: {summary['sample_size']}")

    print("\nAverage metrics for ORIGINAL conversations:")
    for metric, value in summary['original_avg'].items():
        if isinstance(value, float):
            print(f"  {metric}: {value:.2f}")
        else:
            print(f"  {metric}: {value}")

    print("\nAverage metrics for GENALPHA conversations:")
    for metric, value in summary['genalpha_avg'].items():
        if isinstance(value, float):
            print(f"  {metric}: {value:.2f}")
        else:
            print(f"  {metric}: {value}")

    print("\nAverage differences (GenAlpha - Original):")
    for metric, value in summary['differences_avg'].items():
        if isinstance(value, float):
            print(f"  {metric}: {value:+.2f} (±{summary['differences_std'][metric]:.2f})")

    print("\n" + "="*60)
    print("\nKey findings:")
    print("- Check if model maintains empathy with GenAlpha speak")
    print("- Assess if understanding drops with informal language")
    print("- Evaluate if model adapts communication style")
    print("="*60)


if __name__ == "__main__":
    main()
