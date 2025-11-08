"""
GenAlpha Therapy Evaluation Framework

A framework for evaluating how LLM-based therapy models respond to
Gen Alpha speaking patterns and informal language.
"""

from .genalpha_converter import GenAlphaConverter, convert_conversation
from .evaluator import (
    TherapyEvaluator,
    ModelInterface,
    OpenAIModelInterface,
    AnthropicModelInterface,
    EvaluationMetrics,
    aggregate_results
)

__version__ = "0.1.0"

__all__ = [
    "GenAlphaConverter",
    "convert_conversation",
    "TherapyEvaluator",
    "ModelInterface",
    "OpenAIModelInterface",
    "AnthropicModelInterface",
    "EvaluationMetrics",
    "aggregate_results",
]
