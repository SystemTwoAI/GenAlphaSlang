# GenAlpha Conversion Examples

This document shows real examples from the processed therapy dataset.

## Dataset Overview

- **Total conversations processed**: 100
- **Successfully converted**: 96 (4 failed due to special characters)
- **Average turns per conversation**: 16.2
- **Average patient turns**: 8.1
- **Conversion intensity**: 0.7 (moderate)

## Example Conversions

### Example 1: Hobby Discovery

**Original Patient Response:**
> "I'm feeling really sad lately, Alex. I've been trying to find a new hobby to lift my spirits, but I'm not very confident in myself."

**GenAlpha Version:**
> "I'm feeling fr sad lately, Alex. I've been trying to find a new hobby to lift my spirits, but I'm not fr confident in myself..."

**Changes Applied:**
- "really" → "fr" (for real)
- Added "..." for casual punctuation

---

### Example 2: Health Concerns

**Original Patient Response:**
> "Hi Alex! I'm feeling really worried and conflicted about some health issues I've been experiencing lately. Can we talk about it?"

**GenAlpha Version:**
> "hi Alex! I'm feeling highkey not it and conflicted about some health issues I've been experiencing lately. Can we talk about it?"

**Changes Applied:**
- Lowercase sentence start
- "really worried" → "highkey not it"

---

### Example 3: Anxiety and Peace

**Original Patient Response:**
> "Hi Alex! I've been feeling quite anxious lately, and I'm really longing for a sense of peace and change in my life."

**GenAlpha Version:**
> "ngl Hi Alex! I've been feeling quite lowkey stressing lately, and I'm really longing for a sense of peace and change in my life..."

**Changes Applied:**
- Added "ngl" (not gonna lie) as sentence starter
- "anxious" → "lowkey stressing"
- Added "..." for casual punctuation

---

### Example 4: Trust and Betrayal

**Original Patient Response:**
> "Thank you, Alex. Well, recently I confided in a close friend about a personal matter, hoping they would keep it confidential, but they ended up sharing it with others."

**GenAlpha Version:**
> "Thank you, Alex. Well, recently I confided in a close bro about a personal matter, hoping they would keep it confidential, but they ended up sharing it with others. no cap"

**Changes Applied:**
- "close friend" → "close bro"
- Added "no cap" (not lying) as sentence ender

---

### Example 5: Positive Feelings

**Original Patient Response:**
> "For now, I think that covers everything. I'm feeling more hopeful and excited about taking charge of my health."

**GenAlpha Version:**
> "for now, I think that covers everything. I'm feeling more hopeful and W about taking charge of my health..."

**Changes Applied:**
- Lowercase sentence start
- "excited" → "W" (win)

---

### Example 6: Emotions

**Original Patient Response:**
> "I have a few close friends who I trust and who always lift me up when I'm feeling down."

**GenAlpha Version:**
> "i have a few close friends who I trust and who always lift me up when I'm feeling in my feels. They would definitely be a great support system for me. no cap"

**Changes Applied:**
- Lowercase start
- "feeling down" → "in my feels"
- Added "no cap" as ender

---

## Common Transformations Observed

### Emotional States
- "really sad" → "fr sad"
- "worried" → "highkey not it" / "lowkey stressing"
- "anxious" → "lowkey stressing" / "tweaking"
- "stressed" → "not it" / "tweaking"
- "feeling down" → "in my feels"
- "excited" → "W" (win)
- "good" → "vibing" / "W"

### Intensifiers
- "really" / "very" → "fr", "highkey", "lowkey", "deadass"
- "quite" → "lowkey"

### Sentence Modifiers
- **Starters**: "ngl", "tbh", "lowkey", "fr"
- **Enders**: "no cap", "fr", "for real", "ong"

### Social Terms
- "close friend" → "close bro" / "bestie"
- "great" / "cool" → "hits different" / "bussin"
- "good idea" → "vibing idea" / "hits different suggestion"

### Punctuation Style
- More ellipses ("...")
- Some lowercase sentence starts
- More casual, informal structure

## Therapeutic Content Preservation

**Important**: The conversions maintain the core therapeutic content:
- ✅ Emotional meaning preserved
- ✅ Concerns and issues remain clear
- ✅ Therapeutic relationship intact
- ✅ Therapist responses unchanged

The semantic content of patient concerns is maintained while the communication style is transformed.

## Next Steps: Model Evaluation

Now that we have both original and GenAlpha versions, we can:

1. **Generate model responses** to both versions using various LLMs
2. **Compare quality metrics**:
   - Empathy score
   - Understanding of patient concerns
   - Appropriateness
   - Therapeutic quality
   - Style adaptation

3. **Analyze differences**:
   - Does the model maintain the same empathy with GenAlpha speak?
   - Is there a drop in understanding?
   - Does the model adapt its communication style?
   - Are there biases toward formal language?

## Files Generated

- `results/evaluation_subset.csv` - Original 100 conversations
- `results/evaluation_subset_genalpha.csv` - Converted versions
- `results/dataset_analysis.json` - Dataset statistics

## Usage

To run model evaluation:

```bash
python scripts/run_evaluation.py \
    --input results/evaluation_subset_genalpha.csv \
    --output-dir results \
    --model gpt-4 \
    --original-col "first_patient_original" \
    --genalpha-col "first_patient_genalpha" \
    --therapist-col "first_therapist" \
    --limit 10
```

Note: The full conversation objects are in `conversation_original` and `conversation_genalpha` columns.
