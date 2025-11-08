#!/usr/bin/env python3
"""
Comprehensive dataset quality analysis and benchmark creation.

This script analyzes the full therapy conversations dataset to:
1. Assess overall quality and characteristics
2. Identify conversation topics and themes
3. Analyze complexity and difficulty
4. Create stratified benchmark subsets
5. Generate quality reports
"""

import pandas as pd
import numpy as np
import json
import re
from pathlib import Path
from collections import Counter, defaultdict
import argparse
from typing import Dict, List, Tuple
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


def parse_conversation(conversation_str):
    """Parse conversation string into structured data."""
    try:
        import re
        cleaned = conversation_str.replace("\\'", "'")
        cleaned = re.sub(r'\}\s*\n\s*\{', '},\n{', cleaned)
        conversation = eval(cleaned)
        return conversation
    except Exception as e:
        return []


def extract_turns(conversation):
    """Extract patient and therapist turns."""
    patient_turns = [turn['value'] for turn in conversation if turn['from'] == 'human']
    therapist_turns = [turn['value'] for turn in conversation if turn['from'] == 'gpt']
    return patient_turns, therapist_turns


def analyze_conversation_structure(df: pd.DataFrame) -> Dict:
    """Analyze the structure of conversations."""

    print("Analyzing conversation structure...")

    conversation_lengths = []
    patient_turn_counts = []
    therapist_turn_counts = []
    avg_patient_length = []
    avg_therapist_length = []

    for idx, row in df.iterrows():
        if idx % 1000 == 0:
            print(f"  Processing {idx}/{len(df)}...")

        conv = parse_conversation(row['conversations'])
        if not conv:
            continue

        patient_turns, therapist_turns = extract_turns(conv)

        conversation_lengths.append(len(conv))
        patient_turn_counts.append(len(patient_turns))
        therapist_turn_counts.append(len(therapist_turns))

        if patient_turns:
            avg_patient_length.append(np.mean([len(t) for t in patient_turns]))
        if therapist_turns:
            avg_therapist_length.append(np.mean([len(t) for t in therapist_turns]))

    return {
        'total_conversations': len(df),
        'avg_total_turns': np.mean(conversation_lengths),
        'median_total_turns': np.median(conversation_lengths),
        'min_turns': np.min(conversation_lengths),
        'max_turns': np.max(conversation_lengths),
        'avg_patient_turns': np.mean(patient_turn_counts),
        'avg_therapist_turns': np.mean(therapist_turn_counts),
        'avg_patient_msg_length': np.mean(avg_patient_length),
        'avg_therapist_msg_length': np.mean(avg_therapist_length),
        'turn_distribution': {
            'p25': np.percentile(conversation_lengths, 25),
            'p50': np.percentile(conversation_lengths, 50),
            'p75': np.percentile(conversation_lengths, 75),
            'p90': np.percentile(conversation_lengths, 90),
        }
    }


def extract_topics_and_themes(df: pd.DataFrame, sample_size: int = 1000) -> Dict:
    """Extract common topics and themes from conversations."""

    print(f"\nExtracting topics from {sample_size} conversations...")

    # Sample for efficiency
    sample_df = df.sample(n=min(sample_size, len(df)), random_state=42)

    # Keywords for different therapy topics
    topic_keywords = {
        'anxiety': ['anxious', 'anxiety', 'worry', 'worried', 'nervous', 'panic', 'fear', 'scared'],
        'depression': ['depressed', 'depression', 'sad', 'hopeless', 'empty', 'down', 'low'],
        'relationships': ['relationship', 'partner', 'spouse', 'marriage', 'boyfriend', 'girlfriend', 'divorce'],
        'family': ['family', 'parent', 'mother', 'father', 'sibling', 'brother', 'sister', 'child'],
        'work_stress': ['work', 'job', 'career', 'boss', 'coworker', 'workplace', 'employment'],
        'trauma': ['trauma', 'ptsd', 'abuse', 'assault', 'traumatic'],
        'grief': ['grief', 'loss', 'death', 'died', 'mourning', 'bereaved'],
        'self_esteem': ['self-esteem', 'confidence', 'self-worth', 'insecure', 'inadequate'],
        'addiction': ['addiction', 'substance', 'alcohol', 'drugs', 'drinking', 'using'],
        'health': ['health', 'medical', 'illness', 'disease', 'pain', 'chronic'],
    }

    topic_counts = {topic: 0 for topic in topic_keywords}

    for idx, row in sample_df.iterrows():
        conv = parse_conversation(row['conversations'])
        if not conv:
            continue

        # Get all patient text
        patient_turns, _ = extract_turns(conv)
        patient_text = ' '.join(patient_turns).lower()

        # Count topic occurrences
        for topic, keywords in topic_keywords.items():
            if any(keyword in patient_text for keyword in keywords):
                topic_counts[topic] += 1

    return {
        'topic_distribution': topic_counts,
        'sample_size': len(sample_df)
    }


def assess_conversation_quality(df: pd.DataFrame, sample_size: int = 500) -> Dict:
    """Assess the quality of conversations."""

    print(f"\nAssessing conversation quality from {sample_size} conversations...")

    sample_df = df.sample(n=min(sample_size, len(df)), random_state=42)

    quality_metrics = {
        'complete_conversations': 0,
        'multi_turn_conversations': 0,
        'therapeutic_language_present': 0,
        'avg_therapist_empathy_markers': [],
        'avg_patient_emotional_expression': [],
    }

    # Empathy markers in therapist responses
    empathy_markers = ['understand', 'feel', 'sounds like', 'hear you', 'must be',
                       'appreciate', 'validate', 'acknowledge']

    # Emotional expression in patient responses
    emotion_words = ['feel', 'feeling', 'felt', 'worried', 'anxious', 'sad',
                     'happy', 'angry', 'frustrated', 'scared', 'excited']

    for idx, row in sample_df.iterrows():
        conv = parse_conversation(row['conversations'])
        if not conv:
            continue

        patient_turns, therapist_turns = extract_turns(conv)

        # Complete conversations (have both opening and closing)
        if len(conv) >= 4 and len(patient_turns) >= 2 and len(therapist_turns) >= 2:
            quality_metrics['complete_conversations'] += 1

        # Multi-turn (more than just one exchange)
        if len(conv) > 4:
            quality_metrics['multi_turn_conversations'] += 1

        # Check for therapeutic language
        therapist_text = ' '.join(therapist_turns).lower()
        if any(marker in therapist_text for marker in empathy_markers):
            quality_metrics['therapeutic_language_present'] += 1

            # Count empathy markers
            empathy_count = sum(therapist_text.count(marker) for marker in empathy_markers)
            quality_metrics['avg_therapist_empathy_markers'].append(empathy_count / len(therapist_turns))

        # Check for emotional expression
        patient_text = ' '.join(patient_turns).lower()
        emotion_count = sum(patient_text.count(word) for word in emotion_words)
        if emotion_count > 0:
            quality_metrics['avg_patient_emotional_expression'].append(emotion_count / len(patient_turns))

    # Calculate averages
    quality_metrics['complete_conversations_pct'] = quality_metrics['complete_conversations'] / len(sample_df) * 100
    quality_metrics['multi_turn_pct'] = quality_metrics['multi_turn_conversations'] / len(sample_df) * 100
    quality_metrics['therapeutic_language_pct'] = quality_metrics['therapeutic_language_present'] / len(sample_df) * 100

    if quality_metrics['avg_therapist_empathy_markers']:
        quality_metrics['avg_empathy_markers_per_turn'] = np.mean(quality_metrics['avg_therapist_empathy_markers'])

    if quality_metrics['avg_patient_emotional_expression']:
        quality_metrics['avg_emotion_words_per_turn'] = np.mean(quality_metrics['avg_patient_emotional_expression'])

    # Clean up raw lists
    del quality_metrics['avg_therapist_empathy_markers']
    del quality_metrics['avg_patient_emotional_expression']

    return quality_metrics


def categorize_by_complexity(df: pd.DataFrame, sample_size: int = 1000) -> Dict:
    """Categorize conversations by complexity."""

    print(f"\nCategorizing by complexity from {sample_size} conversations...")

    sample_df = df.sample(n=min(sample_size, len(df)), random_state=42)

    complexity_categories = {
        'simple': [],  # 2-6 turns, basic issues
        'moderate': [],  # 7-15 turns, exploration
        'complex': [],  # 16+ turns, deep therapeutic work
    }

    for idx, row in sample_df.iterrows():
        conv = parse_conversation(row['conversations'])
        if not conv:
            continue

        conv_length = len(conv)

        if conv_length <= 6:
            complexity_categories['simple'].append(row['id'])
        elif conv_length <= 15:
            complexity_categories['moderate'].append(row['id'])
        else:
            complexity_categories['complex'].append(row['id'])

    return {
        'simple_count': len(complexity_categories['simple']),
        'moderate_count': len(complexity_categories['moderate']),
        'complex_count': len(complexity_categories['complex']),
        'simple_pct': len(complexity_categories['simple']) / len(sample_df) * 100,
        'moderate_pct': len(complexity_categories['moderate']) / len(sample_df) * 100,
        'complex_pct': len(complexity_categories['complex']) / len(sample_df) * 100,
        'sample_ids': {
            'simple': complexity_categories['simple'][:10],
            'moderate': complexity_categories['moderate'][:10],
            'complex': complexity_categories['complex'][:10],
        }
    }


def create_benchmark_subsets(df: pd.DataFrame, output_dir: Path) -> Dict:
    """Create stratified benchmark subsets."""

    print("\nCreating benchmark subsets...")

    # Create different benchmark sets
    benchmarks = {}

    # 1. Mini benchmark (50 conversations) - quick testing
    mini = df.sample(n=50, random_state=42)
    mini.to_csv(output_dir / 'benchmark_mini_50.csv', index=False)
    benchmarks['mini'] = {'size': 50, 'file': 'benchmark_mini_50.csv'}

    # 2. Standard benchmark (200 conversations) - regular evaluation
    standard = df.sample(n=200, random_state=42)
    standard.to_csv(output_dir / 'benchmark_standard_200.csv', index=False)
    benchmarks['standard'] = {'size': 200, 'file': 'benchmark_standard_200.csv'}

    # 3. Comprehensive benchmark (500 conversations) - thorough evaluation
    comprehensive = df.sample(n=500, random_state=42)
    comprehensive.to_csv(output_dir / 'benchmark_comprehensive_500.csv', index=False)
    benchmarks['comprehensive'] = {'size': 500, 'file': 'benchmark_comprehensive_500.csv'}

    # 4. Stratified by complexity (100 each category)
    print("  Creating complexity-stratified benchmark...")

    # Categorize all conversations by length
    conv_lengths = []
    conv_ids = []

    for idx, row in df.iterrows():
        if idx % 1000 == 0:
            print(f"    Processing {idx}/{len(df)}...")
        conv = parse_conversation(row['conversations'])
        if conv:
            conv_lengths.append(len(conv))
            conv_ids.append(idx)

    df_with_length = df.iloc[conv_ids].copy()
    df_with_length['conv_length'] = conv_lengths

    # Categorize
    df_simple = df_with_length[df_with_length['conv_length'] <= 6]
    df_moderate = df_with_length[(df_with_length['conv_length'] > 6) & (df_with_length['conv_length'] <= 15)]
    df_complex = df_with_length[df_with_length['conv_length'] > 15]

    # Sample from each
    stratified = pd.concat([
        df_simple.sample(n=min(100, len(df_simple)), random_state=42),
        df_moderate.sample(n=min(100, len(df_moderate)), random_state=42),
        df_complex.sample(n=min(100, len(df_complex)), random_state=42),
    ])

    stratified.drop('conv_length', axis=1, inplace=True)
    stratified.to_csv(output_dir / 'benchmark_stratified_300.csv', index=False)
    benchmarks['stratified'] = {
        'size': len(stratified),
        'file': 'benchmark_stratified_300.csv',
        'simple': len(df_simple.sample(n=min(100, len(df_simple)), random_state=42)),
        'moderate': len(df_moderate.sample(n=min(100, len(df_moderate)), random_state=42)),
        'complex': len(df_complex.sample(n=min(100, len(df_complex)), random_state=42)),
    }

    return benchmarks


def main():
    parser = argparse.ArgumentParser(description="Analyze dataset and create benchmarks")
    parser.add_argument("--data-file", type=Path,
                       default=Path("data/chunks/train.csv"),
                       help="Path to full dataset (will reassemble from chunks if needed)")
    parser.add_argument("--output-dir", type=Path,
                       default=Path("results"),
                       help="Directory to save analysis and benchmarks")
    parser.add_argument("--sample-size", type=int, default=1000,
                       help="Sample size for detailed analysis (default: 1000)")

    args = parser.parse_args()

    # Create output directory
    args.output_dir.mkdir(parents=True, exist_ok=True)

    # Load or reassemble dataset
    if not args.data_file.exists():
        print("Dataset not found. Checking for chunks...")
        chunks_dir = Path("data/chunks/train")
        if chunks_dir.exists():
            print("Reassembling from chunks...")
            import subprocess
            subprocess.run(["python", str(chunks_dir / "reassemble_train.py")])
            args.data_file = Path("data/chunks/train.csv")
        else:
            raise FileNotFoundError("Dataset not found and no chunks available")

    print(f"Loading dataset from {args.data_file}...")
    df = pd.read_csv(args.data_file)
    print(f"Loaded {len(df)} conversations\n")

    # Run analyses
    analysis_results = {}

    # 1. Structure analysis
    analysis_results['structure'] = analyze_conversation_structure(df)

    # 2. Topic analysis
    analysis_results['topics'] = extract_topics_and_themes(df, args.sample_size)

    # 3. Quality assessment
    analysis_results['quality'] = assess_conversation_quality(df, args.sample_size // 2)

    # 4. Complexity categorization
    analysis_results['complexity'] = categorize_by_complexity(df, args.sample_size)

    # 5. Create benchmarks
    analysis_results['benchmarks'] = create_benchmark_subsets(df, args.output_dir)

    # Save analysis results
    output_file = args.output_dir / "dataset_quality_analysis.json"
    with open(output_file, 'w') as f:
        json.dump(analysis_results, f, indent=2, default=str)

    print(f"\n{'='*70}")
    print("ANALYSIS COMPLETE")
    print(f"{'='*70}")
    print(f"\nResults saved to: {output_file}")
    print(f"\nBenchmark datasets created:")
    for name, info in analysis_results['benchmarks'].items():
        print(f"  - {name}: {info['size']} conversations -> {info['file']}")

    # Print summary
    print(f"\n{'='*70}")
    print("QUALITY SUMMARY")
    print(f"{'='*70}")
    print(f"\nDataset Size: {analysis_results['structure']['total_conversations']:,} conversations")
    print(f"Avg Turns per Conversation: {analysis_results['structure']['avg_total_turns']:.1f}")
    print(f"Complete Conversations: {analysis_results['quality']['complete_conversations_pct']:.1f}%")
    print(f"Therapeutic Language Present: {analysis_results['quality']['therapeutic_language_pct']:.1f}%")

    print(f"\nTop Topics:")
    topics = analysis_results['topics']['topic_distribution']
    sorted_topics = sorted(topics.items(), key=lambda x: x[1], reverse=True)[:5]
    for topic, count in sorted_topics:
        pct = count / analysis_results['topics']['sample_size'] * 100
        print(f"  - {topic}: {pct:.1f}%")

    print(f"\nComplexity Distribution:")
    print(f"  - Simple (2-6 turns): {analysis_results['complexity']['simple_pct']:.1f}%")
    print(f"  - Moderate (7-15 turns): {analysis_results['complexity']['moderate_pct']:.1f}%")
    print(f"  - Complex (16+ turns): {analysis_results['complexity']['complex_pct']:.1f}%")


if __name__ == "__main__":
    main()
