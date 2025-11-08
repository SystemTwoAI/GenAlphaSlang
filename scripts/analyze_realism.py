#!/usr/bin/env python3
"""
Analyze therapy conversations for realism and quality.

Author: Manisha Mehta (manisha.mehta@systemtwoai.com)
Date: November 2025
"""

import json
import pandas as pd
import re
from pathlib import Path
from collections import Counter, defaultdict
import random


def parse_conversation(conversation_str):
    """Parse conversation string into list of dicts."""
    try:
        cleaned = conversation_str.replace("\\'", "'")
        cleaned = re.sub(r'\}\s*\n\s*\{', '},\n{', cleaned)
        conversation = eval(cleaned)
        return conversation
    except Exception as e:
        return []


def analyze_linguistic_patterns(conversations_sample):
    """Analyze linguistic patterns that might indicate synthetic text."""

    patterns = {
        'formulaic_starts': defaultdict(int),
        'repetitive_phrases': defaultdict(int),
        'therapist_questions': [],
        'patient_disclosures': [],
        'avg_word_diversity': [],
    }

    for conv in conversations_sample:
        therapist_msgs = [msg['value'] for msg in conv if msg.get('from') == 'gpt']
        patient_msgs = [msg['value'] for msg in conv if msg.get('from') == 'human']

        # Check for formulaic starts in therapist responses
        for msg in therapist_msgs:
            first_words = ' '.join(msg.split()[:3]).lower()
            patterns['formulaic_starts'][first_words] += 1

        # Check for repetitive phrases (3+ word sequences)
        all_text = ' '.join(therapist_msgs + patient_msgs).lower()
        words = all_text.split()
        for i in range(len(words) - 2):
            trigram = ' '.join(words[i:i+3])
            if len(trigram) > 10:  # Skip very short sequences
                patterns['repetitive_phrases'][trigram] += 1

        # Collect question patterns
        for msg in therapist_msgs:
            questions = [s.strip() for s in msg.split('?') if s.strip()]
            patterns['therapist_questions'].extend(questions[:1])  # First question

        # Calculate word diversity (unique words / total words)
        if words:
            unique_words = len(set(words))
            total_words = len(words)
            patterns['avg_word_diversity'].append(unique_words / total_words)

    return patterns


def analyze_therapeutic_quality(conversations_sample):
    """Analyze therapeutic techniques and quality."""

    quality_metrics = {
        'empathy_markers': 0,
        'reflection_statements': 0,
        'open_questions': 0,
        'closed_questions': 0,
        'validations': 0,
        'reframes': 0,
        'summarizations': 0,
        'total_therapist_turns': 0,
    }

    empathy_phrases = [
        'i understand', 'i hear', 'that sounds', 'it seems', 'it must',
        'i can imagine', 'i appreciate', 'that makes sense'
    ]

    reflection_phrases = [
        'you mentioned', 'you said', 'you feel', 'you\'re feeling',
        'sounds like you', 'it seems like you'
    ]

    validation_phrases = [
        'that\'s valid', 'that makes sense', 'it\'s understandable',
        'it\'s normal', 'that\'s a common', 'you\'re not alone'
    ]

    reframe_phrases = [
        'another way', 'from a different', 'perspective',
        'what if', 'have you considered', 'could it be'
    ]

    summary_phrases = [
        'so what i\'m hearing', 'let me make sure', 'to summarize',
        'it sounds like overall', 'from what you\'ve shared'
    ]

    for conv in conversations_sample:
        therapist_msgs = [msg['value'] for msg in conv if msg.get('from') == 'gpt']
        quality_metrics['total_therapist_turns'] += len(therapist_msgs)

        for msg in therapist_msgs:
            msg_lower = msg.lower()

            # Count empathy markers
            if any(phrase in msg_lower for phrase in empathy_phrases):
                quality_metrics['empathy_markers'] += 1

            # Count reflections
            if any(phrase in msg_lower for phrase in reflection_phrases):
                quality_metrics['reflection_statements'] += 1

            # Count validations
            if any(phrase in msg_lower for phrase in validation_phrases):
                quality_metrics['validations'] += 1

            # Count reframes
            if any(phrase in msg_lower for phrase in reframe_phrases):
                quality_metrics['reframes'] += 1

            # Count summarizations
            if any(phrase in msg_lower for phrase in summary_phrases):
                quality_metrics['summarizations'] += 1

            # Count questions
            questions = msg.count('?')
            # Heuristic: questions with "how", "what", "why", etc are open
            open_q = len(re.findall(r'\b(how|what|why|tell me|describe|explain)\b.*\?', msg_lower))
            quality_metrics['open_questions'] += open_q
            quality_metrics['closed_questions'] += (questions - open_q)

    return quality_metrics


def analyze_coherence(conversations_sample):
    """Analyze conversation coherence and flow."""

    coherence_metrics = {
        'follows_context': 0,
        'non_sequiturs': 0,
        'topic_shifts': 0,
        'avg_conversation_depth': [],
    }

    for conv in conversations_sample:
        if len(conv) < 4:
            continue

        # Simple heuristic: check if therapist responses reference patient's previous message
        coherent_count = 0
        non_sequitur_count = 0

        for i in range(1, len(conv)):
            if conv[i].get('from') == 'gpt' and i > 0 and conv[i-1].get('from') == 'human':
                patient_msg = conv[i-1]['value'].lower()
                therapist_msg = conv[i]['value'].lower()

                # Extract key content words from patient message
                patient_words = set(re.findall(r'\b\w{4,}\b', patient_msg))
                # Remove common words
                stop_words = {'that', 'this', 'with', 'have', 'from', 'they', 'will', 'would', 'could', 'about', 'there', 'their', 'when', 'what', 'where', 'which', 'while'}
                patient_words = patient_words - stop_words

                # Check if therapist references patient's words
                therapist_words = set(re.findall(r'\b\w{4,}\b', therapist_msg))
                overlap = len(patient_words & therapist_words)

                if overlap >= 1 or any(phrase in therapist_msg for phrase in ['you mentioned', 'you said', 'you feel']):
                    coherent_count += 1
                else:
                    # Check if it's a generic empathy/question (not necessarily a non-sequitur)
                    if not any(phrase in therapist_msg for phrase in ['understand', 'tell me more', 'how', 'what']):
                        non_sequitur_count += 1

        total_responses = sum(1 for msg in conv if msg.get('from') == 'gpt')
        if total_responses > 0:
            coherence_metrics['follows_context'] += coherent_count
            coherence_metrics['non_sequiturs'] += non_sequitur_count

            # Depth: how many turns stay on similar topics
            coherence_metrics['avg_conversation_depth'].append(coherent_count / total_responses)

    return coherence_metrics


def sample_and_display_conversations(df, n=5):
    """Sample and display conversations for manual inspection."""

    print("\n" + "="*80)
    print(f"SAMPLE CONVERSATIONS FOR MANUAL INSPECTION (n={n})")
    print("="*80)

    samples = df.sample(n=min(n, len(df)))

    for idx, row in samples.iterrows():
        conv = parse_conversation(row['conversations'])

        print(f"\n{'-'*80}")
        print(f"Conversation ID: {row.get('id', 'N/A')}")
        print(f"Turns: {len(conv)}")
        print(f"{'-'*80}")

        for i, msg in enumerate(conv[:8]):  # Show first 8 turns
            role = "PATIENT" if msg.get('from') == 'human' else "THERAPIST"
            value = msg.get('value', '')[:200]  # Truncate long messages
            print(f"\n{role}: {value}{'...' if len(msg.get('value', '')) > 200 else ''}")

        if len(conv) > 8:
            print(f"\n... ({len(conv) - 8} more turns)")


def analyze_realism():
    """Main analysis function."""
    project_root = Path(__file__).parent.parent

    print("="*80)
    print("THERAPY CONVERSATION REALISM ANALYSIS")
    print("="*80)

    # Use comprehensive benchmark for analysis
    benchmark_file = project_root / 'results' / 'benchmark_comprehensive_500.csv'
    print(f"\nAnalyzing: {benchmark_file.name}")

    df = pd.read_csv(benchmark_file)
    print(f"Total conversations: {len(df)}")

    # Parse all conversations
    print("\nParsing conversations...")
    conversations = [parse_conversation(row['conversations']) for _, row in df.iterrows()]
    conversations = [c for c in conversations if len(c) >= 4]  # Filter valid conversations

    print(f"Valid conversations: {len(conversations)}")

    # Sample for detailed analysis
    sample_size = min(100, len(conversations))
    conversations_sample = random.sample(conversations, sample_size)

    # 1. Linguistic pattern analysis
    print("\n" + "="*80)
    print("1. LINGUISTIC PATTERN ANALYSIS")
    print("="*80)

    patterns = analyze_linguistic_patterns(conversations_sample)

    print(f"\nWord Diversity: {sum(patterns['avg_word_diversity']) / len(patterns['avg_word_diversity']):.3f}")
    print("  (Higher = more varied vocabulary; 0.3-0.6 is typical for natural text)")

    print(f"\nMost Common Therapist Opening Phrases (top 10):")
    for phrase, count in Counter(patterns['formulaic_starts']).most_common(10):
        if count > 2:
            print(f"  '{phrase}...': {count} times")

    print(f"\nMost Repeated Phrases (top 10):")
    for phrase, count in Counter(patterns['repetitive_phrases']).most_common(10):
        if count > 3:
            print(f"  '{phrase}': {count} times")

    # 2. Therapeutic quality analysis
    print("\n" + "="*80)
    print("2. THERAPEUTIC QUALITY ANALYSIS")
    print("="*80)

    quality = analyze_therapeutic_quality(conversations_sample)

    total_turns = quality['total_therapist_turns']
    print(f"\nTotal therapist turns analyzed: {total_turns}")
    print(f"\nTechnique Usage (per turn):")
    print(f"  Empathy markers:       {quality['empathy_markers']/total_turns:.2f}")
    print(f"  Reflection statements: {quality['reflection_statements']/total_turns:.2f}")
    print(f"  Open questions:        {quality['open_questions']/total_turns:.2f}")
    print(f"  Closed questions:      {quality['closed_questions']/total_turns:.2f}")
    print(f"  Validations:           {quality['validations']/total_turns:.2f}")
    print(f"  Reframes:              {quality['reframes']/total_turns:.2f}")
    print(f"  Summarizations:        {quality['summarizations']/total_turns:.2f}")

    print("\nQuality Assessment:")
    empathy_rate = quality['empathy_markers']/total_turns
    if empathy_rate > 0.5:
        print("  ✓ High empathy presence (realistic)")
    elif empathy_rate > 0.3:
        print("  ~ Moderate empathy presence")
    else:
        print("  ✗ Low empathy presence (may seem robotic)")

    question_rate = (quality['open_questions'] + quality['closed_questions'])/total_turns
    if question_rate > 0.4:
        print("  ✓ Good question usage (realistic)")
    elif question_rate > 0.2:
        print("  ~ Moderate question usage")
    else:
        print("  ✗ Low question usage")

    # 3. Coherence analysis
    print("\n" + "="*80)
    print("3. COHERENCE ANALYSIS")
    print("="*80)

    coherence = analyze_coherence(conversations_sample)

    total_follows = coherence['follows_context']
    total_non_seq = coherence['non_sequiturs']

    print(f"\nContextual following: {total_follows} responses")
    print(f"Potential non-sequiturs: {total_non_seq} responses")

    if coherence['avg_conversation_depth']:
        avg_depth = sum(coherence['avg_conversation_depth']) / len(coherence['avg_conversation_depth'])
        print(f"Average conversation depth: {avg_depth:.2f}")
        print("  (Proportion of responses that reference previous context)")

        if avg_depth > 0.5:
            print("  ✓ High coherence (realistic)")
        elif avg_depth > 0.3:
            print("  ~ Moderate coherence")
        else:
            print("  ✗ Low coherence (conversations may feel disjointed)")

    # 4. Sample conversations for manual inspection
    sample_and_display_conversations(df, n=3)

    # Overall assessment
    print("\n" + "="*80)
    print("OVERALL REALISM ASSESSMENT")
    print("="*80)

    realism_score = 0
    max_score = 5

    # Criteria
    if empathy_rate > 0.3:
        realism_score += 1
        print("✓ Adequate empathy presence")
    else:
        print("✗ Low empathy presence")

    if question_rate > 0.2:
        realism_score += 1
        print("✓ Adequate question usage")
    else:
        print("✗ Low question usage")

    if coherence['avg_conversation_depth'] and avg_depth > 0.3:
        realism_score += 1
        print("✓ Adequate coherence")
    else:
        print("✗ Low coherence")

    word_div = sum(patterns['avg_word_diversity']) / len(patterns['avg_word_diversity'])
    if word_div > 0.3:
        realism_score += 1
        print("✓ Good word diversity")
    else:
        print("✗ Low word diversity")

    # Check for excessive repetition
    max_repetition = max(patterns['repetitive_phrases'].values()) if patterns['repetitive_phrases'] else 0
    if max_repetition < 10:
        realism_score += 1
        print("✓ Low phrase repetition")
    else:
        print("✗ High phrase repetition detected")

    print(f"\nRealism Score: {realism_score}/{max_score}")

    if realism_score >= 4:
        print("Assessment: HIGH REALISM - Conversations appear natural and therapeutic")
    elif realism_score >= 3:
        print("Assessment: MODERATE REALISM - Generally acceptable but some synthetic patterns")
    else:
        print("Assessment: LOW REALISM - Significant synthetic patterns detected")

    # Save results
    results = {
        'linguistic_patterns': {
            'word_diversity': float(word_div),
            'top_formulaic_starts': dict(Counter(patterns['formulaic_starts']).most_common(10)),
            'top_repeated_phrases': dict(Counter(patterns['repetitive_phrases']).most_common(10)),
        },
        'therapeutic_quality': {
            'empathy_rate': float(empathy_rate),
            'question_rate': float(question_rate),
            'open_question_rate': float(quality['open_questions']/total_turns),
            'reflection_rate': float(quality['reflection_statements']/total_turns),
            'validation_rate': float(quality['validations']/total_turns),
        },
        'coherence': {
            'avg_depth': float(avg_depth) if coherence['avg_conversation_depth'] else 0,
            'follows_context': int(total_follows),
            'non_sequiturs': int(total_non_seq),
        },
        'overall': {
            'realism_score': realism_score,
            'max_score': max_score,
            'assessment': 'HIGH' if realism_score >= 4 else ('MODERATE' if realism_score >= 3 else 'LOW')
        }
    }

    output_file = project_root / 'results' / 'realism_analysis.json'
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\nDetailed results saved to {output_file}")


if __name__ == '__main__':
    random.seed(42)
    analyze_realism()
