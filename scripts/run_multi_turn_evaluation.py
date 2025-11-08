#!/usr/bin/env python3
"""
Run automated multi-turn evaluations with LLMs.

This script automates the evaluation process by having LLMs respond
to each turn sequentially.

Author: Manisha Mehta (manisha.mehta@systemtwoai.com)
Date: November 2025
"""

import argparse
import sys
from pathlib import Path
import time
import json

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from multi_turn_evaluator import MultiTurnEvaluator, EvaluationAnalyzer
from utils import parse_conversation, load_benchmark
from llm_evaluation import TherapyLLMEvaluator


def run_llm_evaluation(
    benchmark_file: str,
    conversation_id: str,
    llm_provider: str = 'anthropic',
    llm_model: str = None,
    max_turns: int = 5,
    output_dir: Path = None
):
    """
    Run a complete multi-turn evaluation with an LLM.

    Args:
        benchmark_file: Name of benchmark CSV file
        conversation_id: ID of conversation to evaluate
        llm_provider: LLM provider ('anthropic', 'openai', 'test')
        llm_model: Model name
        max_turns: Number of turns to evaluate
        output_dir: Output directory for sessions
    """
    print("="*80)
    print("AUTOMATED MULTI-TURN LLM EVALUATION")
    print("="*80)

    # Setup
    if not output_dir:
        output_dir = Path(__file__).parent.parent / 'results' / 'evaluation_sessions'

    evaluator = MultiTurnEvaluator(output_dir)

    # Load conversation
    print(f"\nLoading conversation {conversation_id} from {benchmark_file}...")
    df = load_benchmark(benchmark_file)

    row = df[df['id'] == conversation_id].iloc[0]
    conversation = parse_conversation(row['conversations'])

    print(f"Loaded conversation with {len(conversation)} total turns")

    # Create evaluation turns
    print(f"\nCreating {max_turns} evaluation turns...")
    evaluation_turns = evaluator.create_evaluation_turns(
        conversation,
        max_turns=max_turns,
        generate_options=False  # Don't need options for automated evaluation
    )

    print(f"Created {len(evaluation_turns)} evaluation turns")

    # Initialize LLM
    print(f"\nInitializing LLM: {llm_provider} ({llm_model or 'default'})")
    llm_evaluator = TherapyLLMEvaluator(
        provider=llm_provider,
        model=llm_model
    )

    # Start evaluation session
    evaluator_id = f"{llm_provider}-{llm_model or 'default'}"
    print(f"Starting evaluation session for: {evaluator_id}")

    session = evaluator.start_session(
        conversation_id=conversation_id,
        evaluator_id=evaluator_id,
        evaluator_type=llm_provider,
        evaluation_turns=evaluation_turns,
        is_genalpha=False
    )

    print(f"Session ID: {session.session_id}")

    # Run evaluation turn by turn
    print("\n" + "="*80)
    print("RUNNING EVALUATION")
    print("="*80)

    for turn_idx, eval_turn in enumerate(evaluation_turns, 1):
        print(f"\nTurn {turn_idx}/{len(evaluation_turns)}")
        print("-"*80)

        # Build conversation history for LLM
        conversation_history = []
        for hist_turn in eval_turn.conversation_history:
            conversation_history.append({
                'from': 'human' if hist_turn.speaker == 'patient' else 'gpt',
                'value': hist_turn.text
            })

        # Get LLM response
        print("Patient message:")
        print(f"  {eval_turn.patient_message[:100]}...")

        print("\nGetting LLM response...", end=' ')
        start_time = time.time()

        try:
            response_text, metadata = llm_evaluator.get_therapist_response(
                conversation_history
            )
            response_time = time.time() - start_time

            print("✓")
            print(f"Response time: {response_time:.2f}s")
            print(f"\nLLM Response:")
            print(f"  {response_text[:150]}...")

            # Submit response
            evaluator.submit_response(
                turn_number=eval_turn.turn_number,
                response_text=response_text,
                response_type='free_form',
                response_time_seconds=response_time,
                metadata=metadata
            )

            # Rate limiting
            time.sleep(1)

        except Exception as e:
            print(f"✗ Error: {str(e)}")
            # Continue to next turn

    # Completion
    print("\n" + "="*80)
    print("EVALUATION COMPLETE")
    print("="*80)

    print(f"\nSession ID: {session.session_id}")
    print(f"Responses submitted: {len(session.responses)}/{session.max_turns}")
    print(f"Status: {session.status}")

    print(f"\nSession saved to: {output_dir}/session_{session.session_id}.json")

    return session


def batch_evaluate(
    benchmark_file: str,
    num_conversations: int,
    llm_provider: str = 'anthropic',
    llm_model: str = None,
    max_turns: int = 5
):
    """
    Run evaluations on multiple conversations.

    Args:
        benchmark_file: Name of benchmark CSV file
        num_conversations: Number of conversations to evaluate
        llm_provider: LLM provider
        llm_model: Model name
        max_turns: Number of turns per conversation
    """
    print("="*80)
    print("BATCH MULTI-TURN EVALUATION")
    print("="*80)

    df = load_benchmark(benchmark_file)

    # Sample conversations
    sample_conversations = df.sample(n=min(num_conversations, len(df)), random_state=42)

    print(f"\nEvaluating {len(sample_conversations)} conversations")
    print(f"Provider: {llm_provider}")
    print(f"Model: {llm_model or 'default'}")
    print(f"Turns per conversation: {max_turns}")

    results = []

    for idx, (_, row) in enumerate(sample_conversations.iterrows(), 1):
        conversation_id = row['id']

        print(f"\n{'='*80}")
        print(f"Conversation {idx}/{len(sample_conversations)}: {conversation_id}")
        print(f"{'='*80}")

        try:
            session = run_llm_evaluation(
                benchmark_file=benchmark_file,
                conversation_id=conversation_id,
                llm_provider=llm_provider,
                llm_model=llm_model,
                max_turns=max_turns
            )

            results.append({
                'conversation_id': conversation_id,
                'session_id': session.session_id,
                'status': session.status,
                'responses': len(session.responses)
            })

        except Exception as e:
            print(f"\n✗ Failed: {str(e)}")
            results.append({
                'conversation_id': conversation_id,
                'error': str(e)
            })

    # Summary
    print("\n" + "="*80)
    print("BATCH EVALUATION SUMMARY")
    print("="*80)

    successful = len([r for r in results if 'error' not in r])
    print(f"\nSuccessful: {successful}/{len(results)}")

    for result in results:
        if 'error' in result:
            print(f"  ✗ {result['conversation_id']}: {result['error']}")
        else:
            print(f"  ✓ {result['conversation_id']}: {result['status']} ({result['responses']} responses)")


def main():
    parser = argparse.ArgumentParser(
        description='Run automated multi-turn LLM evaluations'
    )

    subparsers = parser.add_subparsers(dest='command', help='Command to run')

    # Single evaluation
    single_parser = subparsers.add_parser('single', help='Evaluate a single conversation')
    single_parser.add_argument('--benchmark', type=str, default='benchmark_mini_50.csv',
                               help='Benchmark file name')
    single_parser.add_argument('--conversation-id', type=str, required=True,
                               help='Conversation ID to evaluate')
    single_parser.add_argument('--provider', type=str, default='test',
                               choices=['anthropic', 'openai', 'test'],
                               help='LLM provider')
    single_parser.add_argument('--model', type=str, default=None,
                               help='Model name')
    single_parser.add_argument('--max-turns', type=int, default=5,
                               help='Number of turns to evaluate')

    # Batch evaluation
    batch_parser = subparsers.add_parser('batch', help='Evaluate multiple conversations')
    batch_parser.add_argument('--benchmark', type=str, default='benchmark_mini_50.csv',
                              help='Benchmark file name')
    batch_parser.add_argument('--num-conversations', type=int, default=3,
                              help='Number of conversations to evaluate')
    batch_parser.add_argument('--provider', type=str, default='test',
                              choices=['anthropic', 'openai', 'test'],
                              help='LLM provider')
    batch_parser.add_argument('--model', type=str, default=None,
                              help='Model name')
    batch_parser.add_argument('--max-turns', type=int, default=5,
                              help='Number of turns per conversation')

    # Analysis
    analysis_parser = subparsers.add_parser('analyze', help='Analyze completed evaluations')
    analysis_parser.add_argument('--evaluator-type', type=str, default=None,
                                 help='Filter by evaluator type')

    args = parser.parse_args()

    if args.command == 'single':
        run_llm_evaluation(
            benchmark_file=args.benchmark,
            conversation_id=args.conversation_id,
            llm_provider=args.provider,
            llm_model=args.model,
            max_turns=args.max_turns
        )

    elif args.command == 'batch':
        batch_evaluate(
            benchmark_file=args.benchmark,
            num_conversations=args.num_conversations,
            llm_provider=args.provider,
            llm_model=args.model,
            max_turns=args.max_turns
        )

    elif args.command == 'analyze':
        output_dir = Path(__file__).parent.parent / 'results' / 'evaluation_sessions'
        analyzer = EvaluationAnalyzer(output_dir)

        stats = analyzer.analyze_response_patterns(args.evaluator_type)

        print("="*80)
        print("EVALUATION ANALYSIS")
        print("="*80)
        print(json.dumps(stats, indent=2))

    else:
        parser.print_help()


if __name__ == '__main__':
    main()
