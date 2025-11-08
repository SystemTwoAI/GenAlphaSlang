#!/usr/bin/env python3
"""
Evaluate LLM responses to therapy conversations (original vs GenAlpha).
Supports multiple LLM providers: Anthropic Claude, OpenAI, etc.

Author: Manisha Mehta (manisha.mehta@systemtwoai.com)
Date: November 2025
"""

import json
import os
import re
import pandas as pd
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import time
from datetime import datetime


def parse_conversation(conversation_str):
    """Parse conversation string into list of dicts."""
    try:
        cleaned = conversation_str.replace("\\'", "'")
        cleaned = re.sub(r'\}\s*\n\s*\{', '},\n{', cleaned)
        conversation = eval(cleaned)
        return conversation
    except Exception as e:
        print(f"Warning: Could not parse conversation: {str(e)[:100]}")
        return []


class TherapyLLMEvaluator:
    """Evaluate LLM responses to therapy conversations."""

    def __init__(self, provider='anthropic', model=None, api_key=None):
        """
        Initialize the evaluator with an LLM provider.

        Args:
            provider: 'anthropic', 'openai', or 'test' (mock responses)
            model: Model name (e.g., 'claude-3-5-sonnet-20241022', 'gpt-4')
            api_key: API key for the provider (or set via environment variable)
        """
        self.provider = provider.lower()
        self.model = model
        self.api_key = api_key or os.getenv(f'{provider.upper()}_API_KEY')

        if self.provider == 'anthropic':
            try:
                import anthropic
                if not self.model:
                    self.model = 'claude-3-5-sonnet-20241022'
                self.client = anthropic.Anthropic(api_key=self.api_key)
            except ImportError:
                raise ImportError("Install anthropic package: pip install anthropic")

        elif self.provider == 'openai':
            try:
                import openai
                if not self.model:
                    self.model = 'gpt-4'
                self.client = openai.OpenAI(api_key=self.api_key)
            except ImportError:
                raise ImportError("Install openai package: pip install openai")

        elif self.provider == 'test':
            # Mock provider for testing
            self.model = 'test-model'
            self.client = None
            print("Using TEST mode - will return mock responses")

        else:
            raise ValueError(f"Unsupported provider: {provider}")

    def create_therapist_prompt(self, conversation_history: List[Dict]) -> str:
        """
        Create a therapist system prompt and format conversation history.

        Args:
            conversation_history: List of {from: 'human'/'gpt', value: str}

        Returns:
            Formatted prompt for the LLM
        """
        system_prompt = """You are an empathetic, professional therapist providing mental health support. Your role is to:

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

        # Format conversation history
        conversation_text = ""
        for msg in conversation_history:
            role = "Patient" if msg['from'] == 'human' else "Therapist"
            conversation_text += f"{role}: {msg['value']}\n\n"

        return system_prompt, conversation_text

    def get_therapist_response(self, conversation_history: List[Dict], max_retries=3) -> Tuple[str, Dict]:
        """
        Get therapist response from LLM.

        Args:
            conversation_history: Previous conversation turns
            max_retries: Number of retries on failure

        Returns:
            (response_text, metadata)
        """
        system_prompt, conversation_text = self.create_therapist_prompt(conversation_history)

        for attempt in range(max_retries):
            try:
                if self.provider == 'anthropic':
                    response = self.client.messages.create(
                        model=self.model,
                        max_tokens=1024,
                        system=system_prompt,
                        messages=[
                            {
                                "role": "user",
                                "content": conversation_text + "\nTherapist:"
                            }
                        ]
                    )
                    response_text = response.content[0].text

                    metadata = {
                        'model': self.model,
                        'usage': {
                            'input_tokens': response.usage.input_tokens,
                            'output_tokens': response.usage.output_tokens,
                        }
                    }

                elif self.provider == 'openai':
                    response = self.client.chat.completions.create(
                        model=self.model,
                        messages=[
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": conversation_text + "\nTherapist:"}
                        ],
                        max_tokens=1024
                    )
                    response_text = response.choices[0].message.content

                    metadata = {
                        'model': self.model,
                        'usage': {
                            'input_tokens': response.usage.prompt_tokens,
                            'output_tokens': response.usage.completion_tokens,
                        }
                    }

                elif self.provider == 'test':
                    # Mock response for testing
                    last_patient_msg = conversation_history[-1]['value'] if conversation_history else ""
                    response_text = f"I hear you. Can you tell me more about {last_patient_msg[:30]}...?"
                    metadata = {
                        'model': self.model,
                        'usage': {'input_tokens': 100, 'output_tokens': 50}
                    }

                return response_text, metadata

            except Exception as e:
                print(f"Attempt {attempt + 1}/{max_retries} failed: {str(e)}")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
                else:
                    raise

    def evaluate_conversation_pair(
        self,
        conversation_id: str,
        original_conversation: List[Dict],
        genalpha_conversation: List[Dict],
        max_turns: int = 5
    ) -> Dict:
        """
        Evaluate LLM responses to both original and GenAlpha versions.

        Args:
            conversation_id: Unique identifier
            original_conversation: Original patient responses
            genalpha_conversation: GenAlpha-converted patient responses
            max_turns: Number of conversation turns to evaluate

        Returns:
            Evaluation results dict
        """
        results = {
            'conversation_id': conversation_id,
            'timestamp': datetime.now().isoformat(),
            'model': self.model,
            'turns': [],
            'summary': {}
        }

        # Extract patient turns from both versions
        original_patient = [msg for msg in original_conversation if msg['from'] == 'human']
        genalpha_patient = [msg for msg in genalpha_conversation if msg['from'] == 'human']

        num_turns = min(len(original_patient), len(genalpha_patient), max_turns)

        print(f"\nEvaluating conversation {conversation_id}")
        print(f"Processing {num_turns} turns...")

        for turn_idx in range(num_turns):
            print(f"  Turn {turn_idx + 1}/{num_turns}...", end=' ')

            # Build conversation history up to this turn
            original_history = []
            genalpha_history = []

            for i in range(turn_idx + 1):
                original_history.append({
                    'from': 'human',
                    'value': original_patient[i]['value']
                })

                genalpha_history.append({
                    'from': 'human',
                    'value': genalpha_patient[i]['value']
                })

            # Get LLM responses to both versions
            try:
                original_response, original_meta = self.get_therapist_response(original_history)
                time.sleep(1)  # Rate limiting
                genalpha_response, genalpha_meta = self.get_therapist_response(genalpha_history)
                time.sleep(1)

                turn_result = {
                    'turn': turn_idx + 1,
                    'original': {
                        'patient': original_patient[turn_idx]['value'],
                        'therapist': original_response,
                        'metadata': original_meta
                    },
                    'genalpha': {
                        'patient': genalpha_patient[turn_idx]['value'],
                        'therapist': genalpha_response,
                        'metadata': genalpha_meta
                    }
                }

                results['turns'].append(turn_result)
                print("✓")

            except Exception as e:
                print(f"✗ Error: {str(e)}")
                results['turns'].append({
                    'turn': turn_idx + 1,
                    'error': str(e)
                })

        # Calculate summary statistics
        successful_turns = [t for t in results['turns'] if 'error' not in t]
        results['summary'] = {
            'total_turns': num_turns,
            'successful_turns': len(successful_turns),
            'failed_turns': num_turns - len(successful_turns),
            'total_input_tokens': sum(
                t['original']['metadata']['usage']['input_tokens'] +
                t['genalpha']['metadata']['usage']['input_tokens']
                for t in successful_turns
            ),
            'total_output_tokens': sum(
                t['original']['metadata']['usage']['output_tokens'] +
                t['genalpha']['metadata']['usage']['output_tokens']
                for t in successful_turns
            ),
        }

        return results


def run_evaluation(
    benchmark_file: Path,
    output_dir: Path,
    provider: str = 'anthropic',
    model: str = None,
    num_conversations: int = 5,
    max_turns: int = 3
):
    """
    Run evaluation on a benchmark file.

    Args:
        benchmark_file: Path to benchmark CSV with both original and genalpha conversations
        output_dir: Directory to save results
        provider: LLM provider ('anthropic', 'openai', 'test')
        model: Model name
        num_conversations: Number of conversations to evaluate
        max_turns: Number of turns per conversation to evaluate
    """
    print("="*80)
    print("THERAPY LLM EVALUATION")
    print("="*80)
    print(f"\nBenchmark: {benchmark_file.name}")
    print(f"Provider: {provider}")
    print(f"Model: {model or 'default'}")
    print(f"Conversations: {num_conversations}")
    print(f"Turns per conversation: {max_turns}")

    # Load benchmark
    df = pd.read_csv(benchmark_file)
    print(f"\nTotal conversations available: {len(df)}")

    # Check for required columns
    required_cols = ['conversations', 'id']
    if not all(col in df.columns for col in required_cols):
        raise ValueError(f"Benchmark must have columns: {required_cols}")

    # Initialize evaluator
    evaluator = TherapyLLMEvaluator(provider=provider, model=model)

    # Sample conversations
    sample_df = df.sample(n=min(num_conversations, len(df)), random_state=42)

    all_results = []

    for idx, row in sample_df.iterrows():
        conversation_id = row['id']
        conversations = parse_conversation(row['conversations'])

        if len(conversations) < 2:
            print(f"\nSkipping {conversation_id} - insufficient turns")
            continue

        # For this evaluation, we'll use the same conversation for both
        # In a real scenario, you'd have separate 'conversations_genalpha' column
        original_conv = conversations
        genalpha_conv = conversations  # TODO: Replace with actual GenAlpha version

        try:
            result = evaluator.evaluate_conversation_pair(
                conversation_id,
                original_conv,
                genalpha_conv,
                max_turns=max_turns
            )
            all_results.append(result)

        except Exception as e:
            print(f"\nFailed to evaluate {conversation_id}: {str(e)}")

    # Save results
    output_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = output_dir / f"evaluation_results_{provider}_{timestamp}.json"

    with open(output_file, 'w') as f:
        json.dump({
            'metadata': {
                'benchmark': str(benchmark_file),
                'provider': provider,
                'model': model,
                'timestamp': datetime.now().isoformat(),
                'num_conversations': len(all_results),
                'max_turns': max_turns,
            },
            'results': all_results
        }, f, indent=2)

    print(f"\n\nResults saved to: {output_file}")

    # Print summary
    print("\n" + "="*80)
    print("EVALUATION SUMMARY")
    print("="*80)

    total_turns = sum(r['summary']['successful_turns'] for r in all_results)
    total_input = sum(r['summary']['total_input_tokens'] for r in all_results)
    total_output = sum(r['summary']['total_output_tokens'] for r in all_results)

    print(f"Total conversations evaluated: {len(all_results)}")
    print(f"Total turns completed: {total_turns}")
    print(f"Total input tokens: {total_input:,}")
    print(f"Total output tokens: {total_output:,}")


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Evaluate LLM responses to therapy conversations')
    parser.add_argument('--benchmark', type=str, default='results/benchmark_mini_50.csv',
                        help='Path to benchmark CSV file')
    parser.add_argument('--output-dir', type=str, default='results/llm_evaluations',
                        help='Output directory for results')
    parser.add_argument('--provider', type=str, default='test',
                        choices=['anthropic', 'openai', 'test'],
                        help='LLM provider to use')
    parser.add_argument('--model', type=str, default=None,
                        help='Model name (e.g., claude-3-5-sonnet-20241022, gpt-4)')
    parser.add_argument('--num-conversations', type=int, default=3,
                        help='Number of conversations to evaluate')
    parser.add_argument('--max-turns', type=int, default=3,
                        help='Maximum turns per conversation')

    args = parser.parse_args()

    project_root = Path(__file__).parent.parent
    benchmark_file = project_root / args.benchmark
    output_dir = project_root / args.output_dir

    if not benchmark_file.exists():
        print(f"Error: Benchmark file not found: {benchmark_file}")
        exit(1)

    run_evaluation(
        benchmark_file=benchmark_file,
        output_dir=output_dir,
        provider=args.provider,
        model=args.model,
        num_conversations=args.num_conversations,
        max_turns=args.max_turns
    )
