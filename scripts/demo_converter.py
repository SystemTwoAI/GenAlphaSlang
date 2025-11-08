#!/usr/bin/env python3
"""
Demo script to showcase the GenAlpha converter without requiring the full dataset.

This demonstrates the language conversion capabilities with example therapy conversations.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from genalpha_converter import GenAlphaConverter


def main():
    print("="*70)
    print("GenAlpha Speak Converter Demo")
    print("="*70)
    print()

    # Example therapy patient responses
    examples = [
        "I've been feeling really anxious about my exams. I can't sleep and I'm worried I'll fail.",
        "I don't know how to deal with my anger. I get upset over small things.",
        "Nobody understands me. I feel so alone and isolated.",
        "I'm worried about my future. Everything feels uncertain and scary.",
        "I think therapy is helping, but I'm not sure if I'm making real progress.",
        "My friends don't really get what I'm going through with my depression.",
        "I'm really stressed about work. My boss doesn't appreciate anything I do.",
        "I feel like I'm not good enough. Everyone else seems to have it together.",
        "I'm trying to be positive, but it's really hard when everything goes wrong.",
        "I agree with what you said last session about setting boundaries.",
    ]

    # Test with different intensity levels
    intensities = [0.3, 0.7, 1.0]

    for intensity in intensities:
        print(f"\n{'='*70}")
        print(f"Conversion Intensity: {intensity} (0=minimal, 1=maximum)")
        print(f"{'='*70}\n")

        converter = GenAlphaConverter(intensity=intensity, use_llm=False)

        for i, original in enumerate(examples[:3], 1):  # Show first 3 for each intensity
            converted = converter.convert_text(original, context="patient")

            print(f"Example {i}:")
            print(f"  Original:  {original}")
            print(f"  GenAlpha:  {converted}")
            print()

    # Show the LLM prompt that could be used for better conversion
    print(f"\n{'='*70}")
    print("LLM Conversion Prompt Example")
    print(f"{'='*70}\n")

    converter = GenAlphaConverter(use_llm=True)
    example_text = examples[0]

    print("For higher quality conversions, use this prompt with your LLM:")
    print()
    print(converter.get_conversion_prompt(example_text))
    print()

    print(f"{'='*70}")
    print("Demo Complete!")
    print(f"{'='*70}")
    print()
    print("Next steps:")
    print("1. Download the therapy conversations dataset")
    print("2. Run analyze_dataset.py to create an evaluation subset")
    print("3. Run convert_to_genalpha.py on the subset")
    print("4. Compare original vs converted conversations")
    print()


if __name__ == "__main__":
    main()
