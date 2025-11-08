# GenAlpha Therapy Speak Evaluation

Evaluating how LLM-based therapy models respond to Gen Alpha speaking patterns.

## Overview

This project investigates whether therapy-oriented language models maintain the same quality of care when patients use Gen Alpha slang and informal communication styles. Gen Alpha (born ~2010+) has distinctive language patterns influenced by social media and internet culture.

### Research Questions

1. **Do therapy models maintain empathy when patients use Gen Alpha slang?**
2. **Does informal language affect the model's understanding of patient concerns?**
3. **Do models adapt their communication style to match the patient?**
4. **Is there a difference in therapeutic quality between responses to formal vs. informal language?**

## Project Structure

```
GenAlphaSlang/
├── data/                    # Dataset (gitignored - too large)
│   ├── *.csv               # Extracted therapy conversations
│   └── *.zip               # Original dataset archives
├── scripts/                # Processing and evaluation scripts
│   ├── analyze_dataset.py          # Analyze and create subset
│   ├── convert_to_genalpha.py      # Convert to GenAlpha speak
│   └── run_evaluation.py           # Run model evaluation
├── src/                    # Core library code
│   ├── genalpha_converter.py       # GenAlpha language converter
│   └── evaluator.py                # Evaluation framework
├── notebooks/              # Jupyter notebooks for analysis
├── results/                # Evaluation results and analysis
└── requirements.txt        # Python dependencies
```

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Download Dataset

1. Download the [Synthetic Therapy Conversations Dataset](https://www.kaggle.com/datasets/thedevastator/synthetic-therapy-conversations-dataset) from Kaggle
2. Extract the CSV file(s) to the `data/` directory
3. The data directory is gitignored due to file size

### 3. Set Up API Keys

For model evaluation, you'll need API access to the models you want to test:

```bash
# Create a .env file
echo "OPENAI_API_KEY=your_key_here" >> .env
echo "ANTHROPIC_API_KEY=your_key_here" >> .env
```

## Usage

### Step 1: Analyze Dataset and Create Subset

```bash
python scripts/analyze_dataset.py \
    --data-dir data \
    --output-dir results \
    --subset-size 100
```

This will:
- Analyze the full dataset structure
- Create a representative evaluation subset (100 conversations)
- Save analysis to `results/dataset_analysis.json`
- Save subset to `results/evaluation_subset.csv`

### Step 2: Convert to GenAlpha Speak

```bash
python scripts/convert_to_genalpha.py \
    --input results/evaluation_subset.csv \
    --output results/evaluation_subset_genalpha.csv \
    --intensity 0.7
```

Parameters:
- `--intensity`: How much to transform (0.0-1.0). Higher = more slang
- `--patient-col`: Specify patient column name if auto-detection fails
- `--use-llm`: Use LLM for higher quality conversions (requires API setup)

This creates a dataset with both original and GenAlpha versions of patient responses.

### Step 3: Run Evaluation

```bash
python scripts/run_evaluation.py \
    --input results/evaluation_subset_genalpha.csv \
    --output-dir results \
    --model gpt-4 \
    --original-col "patient_original" \
    --genalpha-col "patient_genalpha" \
    --therapist-col "therapist"
```

This will:
- Generate model responses to both original and GenAlpha patient messages
- Evaluate response quality (empathy, understanding, appropriateness)
- Compare the differences
- Save detailed results and aggregate summary

### Step 4: Analyze Results

Results are saved as:
- `results/evaluation_results_{model}.csv` - Detailed per-conversation results
- `results/evaluation_summary_{model}.json` - Aggregate statistics

## GenAlpha Language Patterns

The converter translates standard English to Gen Alpha speaking style:

### Common Transformations

| Standard | GenAlpha |
|----------|----------|
| "Yes, I agree" | "fr fr" (for real) |
| "No, that's not true" | "nah that's cap" |
| "I'm feeling very sad" | "ngl I'm down bad" |
| "I'm worried about this" | "lowkey stressing about this fr" |
| "That's really cool" | "that's bussin" / "that hits different" |
| "I don't know" | "idk" / "ion know" |
| "To be honest" | "tbh" |
| "Not going to lie" | "ngl" |

### Characteristics
- **Slang vocabulary**: fr, no cap, bussin, mid, vibing, etc.
- **Abbreviations**: ngl, tbh, idk, idc, ong
- **Intensifiers**: lowkey, highkey, deadass
- **Less formal grammar**: Casual sentence structure
- **Internet influence**: Social media and meme-influenced expressions

## Evaluation Metrics

Responses are evaluated on:

1. **Empathy Score (0-5)**: Does the response show understanding and compassion?
2. **Understanding Score (0-5)**: Does the therapist correctly understand the patient's concern?
3. **Appropriateness Score (0-5)**: Is the response professionally appropriate?
4. **Therapeutic Quality (0-5)**: Does it use effective therapeutic techniques?
5. **Addresses Concern**: Does it address the patient's main issue?
6. **Style Adaptation**: Does the model adapt its communication style?

## Example Conversion

**Original conversation:**
```
Patient: "I've been feeling really anxious about my exams. I can't sleep and I'm worried I'll fail."
Therapist: "It sounds like you're experiencing a lot of stress about your upcoming exams..."
```

**GenAlpha version:**
```
Patient: "ngl I've been lowkey tweaking about my exams fr. can't sleep and I'm worried I'll fail no cap"
Therapist: [Model generates response - does it maintain quality?]
```

## Expected Findings

This research may reveal:
- Whether models are less effective with informal language
- If models incorrectly interpret slang as unprofessional or dismissive
- Whether models adapt communication style to patient language
- Potential biases in model training toward formal language

## Contributing

To add new GenAlpha slang patterns:
1. Edit `src/genalpha_converter.py`
2. Add patterns to `slang_replacements` dictionary
3. Test with sample conversions

## Dataset Citation

Dataset: [Synthetic Therapy Conversations](https://www.kaggle.com/datasets/thedevastator/synthetic-therapy-conversations-dataset)
- Source: Kaggle
- Creator: thedevastator
- Published: December 1, 2023

## License

See LICENSE file for details.

## Notes

- The `data/` directory is gitignored due to GitHub's 100MB file size limit
- Dataset files should be stored locally or in external storage
- API calls to LLMs may incur costs - start with small subsets for testing
- The rule-based converter is fast but LLM-based conversion produces better quality

## Next Steps

1. **Implement LLM-based conversion**: Better quality than rule-based
2. **Add more models**: Test GPT-3.5, Claude, Llama, etc.
3. **Human evaluation**: Verify automated metrics with human judges
4. **Topic analysis**: Do certain topics show bigger differences?
5. **Intervention effectiveness**: Does GenAlpha language affect therapeutic outcomes?