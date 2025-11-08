"""
Common utilities for GenAlpha Therapy Dataset

Author: Manisha Mehta (manisha.mehta@systemtwoai.com)
Date: November 2025
"""

import re
from typing import List, Dict, Optional
from pathlib import Path


def parse_conversation(conversation_str: str) -> List[Dict]:
    """
    Parse conversation string into list of dicts.

    Handles the malformed JSON format from the dataset where list
    items are separated by newlines without commas.

    Args:
        conversation_str: String representation of conversation list

    Returns:
        List of conversation turn dicts with 'from' and 'value' keys

    Example:
        >>> conv_str = "[{'from': 'human', 'value': 'Hello'}\\n{'from': 'gpt', 'value': 'Hi'}]"
        >>> parsed = parse_conversation(conv_str)
        >>> len(parsed)
        2
    """
    try:
        # Replace escaped quotes
        cleaned = conversation_str.replace("\\'", "'")

        # Add commas between list items: }\n { becomes },\n {
        cleaned = re.sub(r'\}\s*\n\s*\{', '},\n{', cleaned)

        conversation = eval(cleaned)
        return conversation
    except Exception as e:
        # Return empty list on parse failure
        return []


def validate_conversation(conversation: List[Dict], min_turns: int = 2) -> bool:
    """
    Check if conversation has valid structure.

    Args:
        conversation: List of conversation turns
        min_turns: Minimum number of turns required

    Returns:
        True if conversation is valid, False otherwise
    """
    if not conversation or len(conversation) < min_turns:
        return False

    for turn in conversation:
        if not isinstance(turn, dict):
            return False
        if 'from' not in turn or 'value' not in turn:
            return False
        if turn['from'] not in ['human', 'gpt']:
            return False
        if not isinstance(turn['value'], str):
            return False

    return True


def get_project_root() -> Path:
    """
    Get project root directory.

    Returns:
        Path to project root
    """
    return Path(__file__).parent.parent


def load_benchmark(benchmark_name: str) -> 'pd.DataFrame':
    """
    Load a benchmark file by name.

    Args:
        benchmark_name: Name of benchmark file (e.g., 'benchmark_mini_50.csv')

    Returns:
        pandas DataFrame with benchmark data

    Raises:
        FileNotFoundError: If benchmark file doesn't exist
    """
    import pandas as pd

    project_root = get_project_root()

    # Try results directory first
    benchmark_path = project_root / 'results' / benchmark_name

    if not benchmark_path.exists():
        raise FileNotFoundError(f"Benchmark not found: {benchmark_path}")

    return pd.read_csv(benchmark_path)


def extract_patient_turns(conversation: List[Dict]) -> List[str]:
    """
    Extract only patient turns from conversation.

    Args:
        conversation: Parsed conversation list

    Returns:
        List of patient message strings
    """
    return [
        turn['value'] for turn in conversation
        if turn.get('from') == 'human'
    ]


def extract_therapist_turns(conversation: List[Dict]) -> List[str]:
    """
    Extract only therapist turns from conversation.

    Args:
        conversation: Parsed conversation list

    Returns:
        List of therapist message strings
    """
    return [
        turn['value'] for turn in conversation
        if turn.get('from') == 'gpt'
    ]


def count_turns(conversation: List[Dict]) -> Dict[str, int]:
    """
    Count patient and therapist turns.

    Args:
        conversation: Parsed conversation list

    Returns:
        Dict with 'patient', 'therapist', and 'total' counts
    """
    patient_count = sum(1 for turn in conversation if turn.get('from') == 'human')
    therapist_count = sum(1 for turn in conversation if turn.get('from') == 'gpt')

    return {
        'patient': patient_count,
        'therapist': therapist_count,
        'total': len(conversation)
    }


def format_conversation_for_display(
    conversation: List[Dict],
    max_turns: int = 10,
    truncate_length: int = 200
) -> str:
    """
    Format conversation for human-readable display.

    Args:
        conversation: Parsed conversation list
        max_turns: Maximum turns to display
        truncate_length: Max length for each message

    Returns:
        Formatted conversation string
    """
    lines = []
    turns_shown = 0

    for turn in conversation:
        if turns_shown >= max_turns:
            break

        role = "PATIENT" if turn.get('from') == 'human' else "THERAPIST"
        value = turn.get('value', '').strip()

        # Truncate long messages
        if len(value) > truncate_length:
            value = value[:truncate_length] + '...'

        lines.append(f"{role}: {value}")
        turns_shown += 1

    if len(conversation) > max_turns:
        remaining = len(conversation) - max_turns
        lines.append(f"\n[... {remaining} more turns]")

    return "\n\n".join(lines)


def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    """
    Safely divide two numbers, returning default if denominator is zero.

    Args:
        numerator: Number to divide
        denominator: Number to divide by
        default: Value to return if denominator is zero

    Returns:
        Result of division or default
    """
    return numerator / denominator if denominator != 0 else default
