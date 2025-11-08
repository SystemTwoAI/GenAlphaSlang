#!/usr/bin/env python3
"""
Analyze benchmark coverage to ensure it's representative of the full dataset.
"""

import json
import pandas as pd
from pathlib import Path
import numpy as np


def parse_conversation(conversation_str):
    """Parse conversation string into list of dicts."""
    try:
        import re
        cleaned = conversation_str.replace("\\'", "'")
        cleaned = re.sub(r'\}\s*\n\s*\{', '},\n{', cleaned)
        conversation = eval(cleaned)
        return conversation
    except Exception as e:
        return []


def extract_features(row):
    """Extract features from a conversation."""
    conversation = parse_conversation(row['conversations'])

    # Basic metrics
    num_turns = len(conversation)

    # Count patient vs therapist turns
    patient_turns = sum(1 for msg in conversation if msg.get('from') == 'human')
    therapist_turns = sum(1 for msg in conversation if msg.get('from') == 'gpt')

    # Text lengths
    patient_text = ' '.join([msg.get('value', '') for msg in conversation if msg.get('from') == 'human'])
    therapist_text = ' '.join([msg.get('value', '') for msg in conversation if msg.get('from') == 'gpt'])

    patient_words = len(patient_text.split())
    therapist_words = len(therapist_text.split())
    patient_chars = len(patient_text)
    therapist_chars = len(therapist_text)

    # Topic indicators (simple keyword matching)
    full_text = (patient_text + ' ' + therapist_text).lower()
    topics = {
        'anxiety': any(word in full_text for word in ['anxious', 'anxiety', 'worry', 'worried', 'nervous']),
        'depression': any(word in full_text for word in ['depress', 'sad', 'hopeless', 'worthless']),
        'relationships': any(word in full_text for word in ['relationship', 'partner', 'spouse', 'family', 'friend']),
        'work_stress': any(word in full_text for word in ['work', 'job', 'career', 'boss', 'colleague']),
        'trauma': any(word in full_text for word in ['trauma', 'abuse', 'ptsd', 'flashback']),
        'self_esteem': any(word in full_text for word in ['self-esteem', 'confidence', 'worth', 'inadequate']),
        'grief': any(word in full_text for word in ['grief', 'loss', 'mourning', 'bereavement']),
        'addiction': any(word in full_text for word in ['addiction', 'substance', 'alcohol', 'drug', 'gambling']),
        'health': any(word in full_text for word in ['health', 'medical', 'illness', 'pain', 'chronic'])
    }

    # Therapeutic elements
    has_empathy = any(phrase in therapist_text.lower() for phrase in [
        'understand', 'hear you', 'sounds like', 'must be', 'can imagine',
        'appreciate you sharing', 'thank you for'
    ])

    has_questions = '?' in therapist_text
    has_reflection = any(phrase in therapist_text.lower() for phrase in [
        'it seems', 'it sounds', 'you mentioned', 'you said', 'you feel'
    ])

    # Conversation quality
    is_complete = num_turns >= 4 and patient_turns >= 2 and therapist_turns >= 2

    # Complexity based on turn count
    complexity = 'simple' if num_turns <= 8 else ('moderate' if num_turns <= 16 else 'complex')

    return {
        'num_turns': num_turns,
        'patient_turns': patient_turns,
        'therapist_turns': therapist_turns,
        'patient_words': patient_words,
        'therapist_words': therapist_words,
        'patient_chars': patient_chars,
        'therapist_chars': therapist_chars,
        'total_words': patient_words + therapist_words,
        'avg_patient_words': patient_words / max(patient_turns, 1),
        'avg_therapist_words': therapist_words / max(therapist_turns, 1),
        'avg_patient_chars': patient_chars / max(patient_turns, 1),
        'avg_therapist_chars': therapist_chars / max(therapist_turns, 1),
        'has_empathy': has_empathy,
        'has_questions': has_questions,
        'has_reflection': has_reflection,
        'is_complete': is_complete,
        'complexity': complexity,
        **{f'topic_{k}': v for k, v in topics.items()}
    }


def analyze_coverage():
    """Main analysis function."""
    project_root = Path(__file__).parent.parent

    # Load full dataset stats
    analysis_file = project_root / 'results' / 'dataset_quality_analysis.json'
    with open(analysis_file) as f:
        full_stats = json.load(f)

    print("="*80)
    print("BENCHMARK COVERAGE ANALYSIS")
    print("="*80)
    print(f"\nFull Dataset: {full_stats['structure']['total_conversations']:,} conversations")
    print(f"  Avg turns: {full_stats['structure']['avg_total_turns']:.1f}")
    print(f"  Avg patient message length: {full_stats['structure']['avg_patient_msg_length']:.1f} chars")
    print(f"  Avg therapist message length: {full_stats['structure']['avg_therapist_msg_length']:.1f} chars")

    # Load benchmark files
    benchmarks = {
        'mini_50': project_root / 'results' / 'benchmark_mini_50.csv',
        'standard_200': project_root / 'results' / 'benchmark_standard_200.csv',
        'stratified_300': project_root / 'results' / 'benchmark_stratified_300.csv',
        'comprehensive_500': project_root / 'results' / 'benchmark_comprehensive_500.csv',
    }

    results = {}

    for bench_name, bench_path in benchmarks.items():
        print(f"\n{'='*80}")
        print(f"Analyzing: {bench_name}")
        print(f"{'='*80}")

        benchmark_df = pd.read_csv(bench_path)
        print(f"Benchmark size: {len(benchmark_df)} conversations")

        # Extract features from benchmark
        print("Extracting features...")
        bench_features = benchmark_df.apply(extract_features, axis=1, result_type='expand')

        # Numerical feature comparison
        print("\n" + "-"*80)
        print("NUMERICAL FEATURES")
        print("-"*80)

        metrics = {
            'num_turns': ('Turns per conversation', full_stats['structure']['avg_total_turns']),
            'patient_turns': ('Patient turns', full_stats['structure']['avg_patient_turns']),
            'therapist_turns': ('Therapist turns', full_stats['structure']['avg_therapist_turns']),
            'avg_patient_chars': ('Avg patient message length', full_stats['structure']['avg_patient_msg_length']),
            'avg_therapist_chars': ('Avg therapist message length', full_stats['structure']['avg_therapist_msg_length']),
        }

        feature_comparison = {}
        similar_count = 0

        for feature, (label, full_mean) in metrics.items():
            bench_mean = bench_features[feature].mean()
            bench_median = bench_features[feature].median()
            bench_std = bench_features[feature].std()

            # Calculate relative difference
            rel_diff = abs(bench_mean - full_mean) / full_mean * 100

            # Within 15% is considered similar
            is_similar = rel_diff < 15

            if is_similar:
                similar_count += 1
                status = "✓ SIMILAR"
            elif rel_diff < 25:
                status = "~ MODERATE"
            else:
                status = "✗ DIFFERENT"

            print(f"\n{label}:")
            print(f"  {status:12} (diff={rel_diff:.1f}%)")
            print(f"  Full dataset: {full_mean:.1f}")
            print(f"  Benchmark:    {bench_mean:.1f} (median={bench_median:.1f}, std={bench_std:.1f})")

            feature_comparison[feature] = {
                'full_mean': float(full_mean),
                'benchmark_mean': float(bench_mean),
                'benchmark_median': float(bench_median),
                'benchmark_std': float(bench_std),
                'relative_diff_pct': float(rel_diff),
                'similar': bool(is_similar)
            }

        # Categorical features
        print("\n" + "-"*80)
        print("CATEGORICAL FEATURES")
        print("-"*80)

        # Complexity distribution
        complexity_dist = bench_features['complexity'].value_counts(normalize=True) * 100
        print(f"\nComplexity Distribution:")
        print(f"  Simple:   Bench={complexity_dist.get('simple', 0):.1f}%, Full={full_stats['complexity']['simple_pct']:.1f}%")
        print(f"  Moderate: Bench={complexity_dist.get('moderate', 0):.1f}%, Full={full_stats['complexity']['moderate_pct']:.1f}%")
        print(f"  Complex:  Bench={complexity_dist.get('complex', 0):.1f}%, Full={full_stats['complexity']['complex_pct']:.1f}%")

        # Topic distribution
        print(f"\nTopic Coverage:")
        topic_cols = [col for col in bench_features.columns if col.startswith('topic_')]
        for topic_col in sorted(topic_cols):
            topic_name = topic_col.replace('topic_', '')
            bench_pct = bench_features[topic_col].sum() / len(bench_features) * 100
            # Note: full dataset topic stats are from a sample, so we just report benchmark coverage
            print(f"  {topic_name:15} {bench_pct:5.1f}% of conversations")

        # Quality metrics
        print(f"\nQuality Metrics:")
        complete_pct = bench_features['is_complete'].sum() / len(bench_features) * 100
        empathy_pct = bench_features['has_empathy'].sum() / len(bench_features) * 100
        questions_pct = bench_features['has_questions'].sum() / len(bench_features) * 100
        reflection_pct = bench_features['has_reflection'].sum() / len(bench_features) * 100

        print(f"  Complete conversations: {complete_pct:.1f}% (Full: {full_stats['quality']['complete_conversations_pct']:.1f}%)")
        print(f"  Has empathy markers:    {empathy_pct:.1f}%")
        print(f"  Has questions:          {questions_pct:.1f}%")
        print(f"  Has reflection:         {reflection_pct:.1f}%")

        # Overall coverage score
        coverage_score = similar_count / len(metrics) * 100

        print(f"\n{'='*80}")
        print(f"COVERAGE SCORE: {coverage_score:.1f}%")
        print(f"({similar_count}/{len(metrics)} numerical features within 15% of full dataset)")
        print(f"{'='*80}")

        results[bench_name] = {
            'size': len(benchmark_df),
            'coverage_score': float(coverage_score),
            'similar_features': similar_count,
            'total_features': len(metrics),
            'feature_comparison': feature_comparison,
            'complexity_distribution': {
                'simple': float(complexity_dist.get('simple', 0)),
                'moderate': float(complexity_dist.get('moderate', 0)),
                'complex': float(complexity_dist.get('complex', 0))
            },
            'quality_metrics': {
                'complete_pct': float(complete_pct),
                'empathy_pct': float(empathy_pct),
                'questions_pct': float(questions_pct),
                'reflection_pct': float(reflection_pct)
            }
        }

    # Save results
    output_file = project_root / 'results' / 'benchmark_coverage_analysis.json'
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\n\nDetailed results saved to {output_file}")

    # Summary
    print("\n" + "="*80)
    print("COVERAGE SUMMARY")
    print("="*80)
    print(f"\n{'Benchmark':<25} {'Size':>8} {'Coverage':>10} {'Status':>12}")
    print("-"*80)
    for bench_name, result in results.items():
        score = result['coverage_score']
        status = "✓ GOOD" if score >= 80 else ("~ OK" if score >= 60 else "✗ POOR")
        print(f"{bench_name:<25} {result['size']:>8} {score:>9.1f}% {status:>12}")

    return results


if __name__ == '__main__':
    analyze_coverage()
