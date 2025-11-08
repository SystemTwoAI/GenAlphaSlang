#!/usr/bin/env python3
"""
Example script demonstrating the use of modular components.

This shows how the refactored code uses shared utilities and therapeutic analysis.

Author: Manisha Mehta (manisha.mehta@systemtwoai.com)
Date: November 2025
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from utils import (
    parse_conversation,
    validate_conversation,
    extract_patient_turns,
    extract_therapist_turns,
    format_conversation_for_display,
    load_benchmark
)
from therapeutic_analysis import TherapeuticAnalyzer


def main():
    """Demonstrate modular analysis."""
    print("="*80)
    print("MODULAR THERAPEUTIC ANALYSIS DEMO")
    print("="*80)

    # Load benchmark using utility function
    print("\n1. Loading benchmark using utils.load_benchmark()...")
    df = load_benchmark('benchmark_mini_50.csv')
    print(f"   Loaded {len(df)} conversations")

    # Get first conversation
    first_row = df.iloc[0]
    print(f"\n2. Parsing conversation {first_row['id']}...")

    # Parse using shared utility
    conversation = parse_conversation(first_row['conversations'])
    print(f"   Parsed {len(conversation)} turns")

    # Validate using shared utility
    is_valid = validate_conversation(conversation, min_turns=4)
    print(f"   Valid conversation: {is_valid}")

    # Extract patient/therapist turns
    patient_turns = extract_patient_turns(conversation)
    therapist_turns = extract_therapist_turns(conversation)
    print(f"   Patient turns: {len(patient_turns)}")
    print(f"   Therapist turns: {len(therapist_turns)}")

    # Display conversation
    print("\n3. Formatted conversation display:")
    print("-"*80)
    formatted = format_conversation_for_display(conversation, max_turns=4)
    print(formatted)

    # Analyze therapeutic quality
    print("\n4. Therapeutic Quality Analysis:")
    print("-"*80)

    analyzer = TherapeuticAnalyzer()
    metrics = analyzer.analyze_conversation(conversation)

    print(f"   Total therapist turns: {metrics['total_therapist_turns']}")
    print(f"   Empathy rate: {metrics['empathy_rate']:.2f}")
    print(f"   Reflection rate: {metrics['reflection_rate']:.2f}")
    print(f"   Validation rate: {metrics['validation_rate']:.2f}")
    print(f"   Question rate: {metrics['question_rate']:.2f}")
    print(f"   Open question rate: {metrics['open_question_rate']:.2f}")

    # Get quality assessment
    rating, feedback = analyzer.assess_quality(metrics)

    print(f"\n5. Quality Assessment:")
    print(f"   Overall Rating: {rating}")
    print(f"   Feedback:")
    for item in feedback:
        print(f"     {item}")

    print("\n" + "="*80)
    print("DEMO COMPLETE")
    print("="*80)

    print("\nKey Benefits of Modular Design:")
    print("  ✓ No code duplication - parse_conversation() used once")
    print("  ✓ Reusable components - TherapeuticAnalyzer can be used anywhere")
    print("  ✓ Easy to test - Each module can be unit tested independently")
    print("  ✓ Maintainable - Bug fixes in one place benefit all scripts")
    print("  ✓ Clear separation - Utils for data, TherapeuticAnalyzer for analysis")


if __name__ == '__main__':
    main()
