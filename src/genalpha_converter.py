"""
GenAlpha Speak Converter

Converts standard text to GenAlpha (Gen Alpha) speaking style.
Gen Alpha refers to people born from ~2010 onwards, with distinctive slang and communication patterns.
"""

import re
from typing import Dict, List, Optional
import random


class GenAlphaConverter:
    """Convert standard text to GenAlpha speaking style."""

    def __init__(self, intensity: float = 0.7, use_llm: bool = True):
        """
        Initialize the converter.

        Args:
            intensity: How much to transform (0.0-1.0). Higher = more slang.
            use_llm: Whether to use LLM for conversions (better quality)
        """
        self.intensity = intensity
        self.use_llm = use_llm

        # GenAlpha vocabulary mappings
        self.slang_replacements = {
            # Affirmations
            r'\b(yes|yeah|yep)\b': ['fr', 'frfr', 'yeah fr', 'fs', 'ong'],
            r'\b(really|very|extremely)\b': ['lowkey', 'highkey', 'deadass', 'fr'],
            r'\b(I agree|I think so|exactly)\b': ['no cap', 'fr fr', 'facts', 'real'],

            # Negations
            r'\b(no|nope)\b': ['nah', 'nah fr', 'cap'],
            r'\b(fake|lying|not true)\b': ['cap', 'cappin'],

            # Expressions
            r'\b(cool|great|awesome|amazing)\b': ['fire', 'bussin', 'slaps', 'hits different', 'goated'],
            r'\b(bad|terrible|awful)\b': ['mid', 'trash', 'ain\'t it'],
            r'\b(weird|strange|odd)\b': ['sus', 'lowkey weird', 'giving weird vibes'],
            r'\b(embarrassing|cringe)\b': ['cringe', 'ick'],

            # Emotions
            r'\b(sad|depressed|down)\b': ['in my feels', 'down bad', 'not vibing'],
            r'\b(angry|mad|upset)\b': ['pressed', 'tight', 'tweaking'],
            r'\b(happy|excited|good)\b': ['vibing', 'living my best life', 'W'],
            r'\b(anxious|worried|stressed)\b': ['lowkey stressing', 'tweaking', 'not it'],

            # Intensifiers
            r'\b(not going to lie)\b': ['ngl'],
            r'\b(to be honest)\b': ['tbh'],
            r'\b(I don\'t know)\b': ['idk', 'ion know'],
            r'\b(I don\'t care)\b': ['idc', 'ion care'],

            # Social
            r'\b(friends|friend)\b': ['bestie', 'homie', 'bro'],
            r'\b(understand|get it)\b': ['catch the vibe', 'feel you', 'understood the assignment'],
            r'\b(ignore|avoiding)\b': ['ghosting', 'left on read'],

            # Descriptors
            r'\b(attractive|good-looking)\b': ['valid', 'ate', 'serving'],
            r'\b(trying too hard)\b': ['doing too much', 'extra'],
            r'\b(stylish|fashionable)\b': ['drip', 'drippy', 'clean'],
        }

        # Sentence modifiers
        self.sentence_starters = ['ngl', 'tbh', 'lowkey', 'highkey', 'fr']
        self.sentence_enders = ['fr', 'no cap', 'ong', 'for real']

        # Punctuation patterns (GenAlpha often uses less formal punctuation)
        self.punctuation_style = {
            'multiple_periods': True,  # "yeah..." instead of "yeah."
            'lowercase_start': True,   # Less capitalization
            'emojis': False,           # We'll keep this off for therapy context
        }

    def convert_text(self, text: str, context: str = "patient") -> str:
        """
        Convert text to GenAlpha speak.

        Args:
            text: Original text
            context: Context of the speaker (patient, therapist, etc.)

        Returns:
            Converted text in GenAlpha style
        """
        if context != "patient":
            # Only convert patient side
            return text

        if self.use_llm:
            # Use LLM-based conversion for better quality
            return self._convert_with_llm(text)
        else:
            # Use rule-based conversion
            return self._convert_rule_based(text)

    def _convert_rule_based(self, text: str) -> str:
        """Rule-based conversion using pattern matching."""
        converted = text

        # Apply slang replacements based on intensity
        for pattern, replacements in self.slang_replacements.items():
            if random.random() < self.intensity:
                replacement = random.choice(replacements)
                converted = re.sub(pattern, replacement, converted, flags=re.IGNORECASE)

        # Maybe add sentence starter
        if random.random() < self.intensity * 0.3:
            starter = random.choice(self.sentence_starters)
            converted = f"{starter} {converted}"

        # Maybe add sentence ender
        if random.random() < self.intensity * 0.3:
            ender = random.choice(self.sentence_enders)
            converted = f"{converted} {ender}"

        # Apply punctuation style
        if self.punctuation_style['lowercase_start'] and random.random() < 0.5:
            converted = converted[0].lower() + converted[1:] if converted else converted

        if self.punctuation_style['multiple_periods']:
            converted = re.sub(r'\.(?!\.\.)$', '...', converted)

        return converted

    def _convert_with_llm(self, text: str) -> str:
        """
        Convert using LLM (to be implemented with actual API calls).
        For now, returns a placeholder that combines rule-based conversion.
        """
        # This is a placeholder - actual implementation would call an LLM API
        # with a prompt like:
        #
        # "Convert the following text to Gen Alpha speaking style while maintaining
        #  the semantic meaning. Gen Alpha style includes: modern slang (fr, no cap,
        #  bussin), abbreviations (ngl, tbh, idk), casual grammar, and internet
        #  influenced language. Keep the emotional content and meaning intact.
        #
        #  Original: {text}
        #  Converted:"

        return self._convert_rule_based(text)

    def get_conversion_prompt(self, text: str) -> str:
        """
        Get the LLM prompt for converting text.
        Use this with your preferred LLM API.
        """
        return f"""Convert the following therapy patient response to Gen Alpha speaking style.

Gen Alpha characteristics:
- Modern slang: fr (for real), no cap (not lying), bussin (great), mid (mediocre), etc.
- Abbreviations: ngl (not gonna lie), tbh (to be honest), idk (I don't know)
- Casual grammar and less formal structure
- Internet/social media influenced expressions
- Common phrases: "lowkey", "highkey", "vibing", "hits different", "down bad"

Important:
- Maintain the EXACT same emotional content and meaning
- Keep the therapeutic context appropriate
- Don't add emoji or excessive informality
- Preserve the core message while changing the style

Original patient response:
"{text}"

Gen Alpha version:"""


def convert_conversation(
    conversation: Dict[str, str],
    converter: GenAlphaConverter,
    patient_key: str = "patient",
    therapist_key: str = "therapist"
) -> Dict[str, str]:
    """
    Convert a conversation dictionary, only transforming patient responses.

    Args:
        conversation: Dict with patient and therapist responses
        converter: GenAlphaConverter instance
        patient_key: Key for patient responses
        therapist_key: Key for therapist responses

    Returns:
        New conversation dict with converted patient responses
    """
    converted = conversation.copy()

    if patient_key in converted:
        converted[f"{patient_key}_original"] = converted[patient_key]
        converted[patient_key] = converter.convert_text(
            converted[patient_key],
            context="patient"
        )

    return converted
