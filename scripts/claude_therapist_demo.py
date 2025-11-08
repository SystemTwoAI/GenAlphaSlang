#!/usr/bin/env python3
"""
Demonstrate how Claude would respond as a therapist to sample conversations.
This script shows example patient messages and demonstrates appropriate therapeutic responses.
"""

import json
import pandas as pd
import re
from pathlib import Path
from typing import List, Dict


def parse_conversation(conversation_str):
    """Parse conversation string into list of dicts."""
    try:
        cleaned = conversation_str.replace("\\'", "'")
        cleaned = re.sub(r'\}\s*\n\s*\{', '},\n{', cleaned)
        conversation = eval(cleaned)
        return conversation
    except Exception as e:
        return []


def format_conversation_for_display(conversation: List[Dict], max_turns: int = 4):
    """Format a conversation for display."""
    lines = []
    turns_shown = 0

    for msg in conversation:
        if turns_shown >= max_turns:
            break

        role = "PATIENT" if msg.get('from') == 'human' else "THERAPIST"
        value = msg.get('value', '').strip()

        lines.append(f"{role}: {value}")
        turns_shown += 1

    if len(conversation) > max_turns:
        lines.append(f"\n[... {len(conversation) - max_turns} more turns]")

    return "\n\n".join(lines)


def create_therapist_system_prompt():
    """Create the system prompt for Claude as a therapist."""
    return """You are an empathetic, professional therapist providing mental health support. Your role is to:

1. Listen actively and validate the patient's feelings
2. Ask thoughtful, open-ended questions to understand their situation better
3. Provide empathy and emotional support
4. Use evidence-based therapeutic techniques (CBT, mindfulness, etc.) when appropriate
5. Help the patient explore their thoughts and feelings
6. Maintain professional boundaries while being warm and supportive

Important guidelines:
- Never diagnose medical conditions
- Recommend professional help when appropriate
- Be non-judgmental and accepting
- Focus on the patient's wellbeing
- Use reflective listening and summarization

Respond naturally as a caring therapist would in a counseling session."""


def demonstrate_responses():
    """Load sample conversations and demonstrate how Claude would respond."""
    project_root = Path(__file__).parent.parent
    benchmark_file = project_root / 'results' / 'benchmark_mini_50.csv'

    if not benchmark_file.exists():
        print(f"Error: Benchmark file not found: {benchmark_file}")
        return

    print("="*80)
    print("CLAUDE THERAPIST DEMONSTRATION")
    print("="*80)
    print("\nThis demonstrates how Claude (without project knowledge) would respond")
    print("to patient messages from the therapy conversation dataset.")
    print("\nSystem Prompt Used:")
    print("-"*80)
    print(create_therapist_system_prompt())
    print("-"*80)

    # Load benchmark
    df = pd.read_csv(benchmark_file)

    # Sample a few conversations
    samples = df.sample(n=3, random_state=42)

    demo_results = []

    for idx, (_, row) in enumerate(samples.iterrows(), 1):
        conversation = parse_conversation(row['conversations'])

        if len(conversation) < 2:
            continue

        print(f"\n{'='*80}")
        print(f"SAMPLE CONVERSATION {idx}: {row['id']}")
        print(f"{'='*80}")

        # Show the original conversation
        print("\nORIGINAL CONVERSATION:")
        print("-"*80)
        print(format_conversation_for_display(conversation, max_turns=6))

        # Extract first patient message for demonstration
        patient_messages = [msg for msg in conversation if msg['from'] == 'human']

        if patient_messages:
            first_patient_msg = patient_messages[0]['value']

            print(f"\n{'='*80}")
            print("DEMONSTRATION: CLAUDE'S RESPONSE TO FIRST PATIENT MESSAGE")
            print(f"{'='*80}")
            print(f"\nPatient's opening message:")
            print(f'"{first_patient_msg}"')

            print(f"\nClaude's therapeutic response would focus on:")
            print("  1. Acknowledging the patient's feelings")
            print("  2. Showing empathy and understanding")
            print("  3. Asking open-ended questions to explore further")
            print("  4. Creating a safe, non-judgmental space")

            # Store for summary
            demo_results.append({
                'conversation_id': row['id'],
                'patient_opening': first_patient_msg,
                'num_turns': len(conversation)
            })

    # Summary
    print(f"\n{'='*80}")
    print("SUMMARY")
    print(f"{'='*80}")
    print(f"\nDemonstrated {len(demo_results)} sample conversations")
    print(f"\nKey therapeutic principles Claude would apply:")
    print("  • Active listening and validation")
    print("  • Empathetic responses")
    print("  • Open-ended questions")
    print("  • Non-judgmental stance")
    print("  • Focus on patient wellbeing")
    print("  • Appropriate boundaries")

    print(f"\n\nNote: To get actual Claude API responses, use the llm_evaluation.py script")
    print("with the --provider anthropic flag and a valid ANTHROPIC_API_KEY.")

    return demo_results


def show_sample_patient_messages():
    """Show sample patient messages from different scenarios."""
    project_root = Path(__file__).parent.parent
    benchmark_file = project_root / 'results' / 'benchmark_mini_50.csv'

    if not benchmark_file.exists():
        print(f"Error: Benchmark file not found: {benchmark_file}")
        return

    df = pd.read_csv(benchmark_file)

    print("\n" + "="*80)
    print("SAMPLE PATIENT MESSAGES FOR CLAUDE TO RESPOND TO")
    print("="*80)

    # Extract diverse patient openings
    patient_openings = []

    for _, row in df.iterrows():
        conversation = parse_conversation(row['conversations'])
        patient_msgs = [msg for msg in conversation if msg['from'] == 'human']

        if patient_msgs:
            patient_openings.append({
                'id': row['id'],
                'opening': patient_msgs[0]['value']
            })

    # Sample 5 diverse examples
    samples = pd.DataFrame(patient_openings).sample(n=5, random_state=42)

    for idx, row in samples.iterrows():
        print(f"\n{'-'*80}")
        print(f"Patient Message {idx+1}:")
        print(f"{'-'*80}")
        print(f'"{row["opening"][:300]}{"..." if len(row["opening"]) > 300 else ""}"')

    print(f"\n{'='*80}")
    print("\nThese are real patient openings from the dataset that Claude would")
    print("respond to with appropriate therapeutic interventions.")


if __name__ == '__main__':
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == '--sample-messages':
        show_sample_patient_messages()
    else:
        demonstrate_responses()
