# Quick Start Guide

Once you have the dataset in the `data/` directory, follow these steps:

## 1. First Look at Your Data

```bash
# Check what files you have
ls -lh data/

# Quick peek at the CSV structure (first 5 rows)
head -5 data/*.csv
```

## 2. Run the Full Pipeline

```bash
# Step 1: Analyze dataset and create evaluation subset
python scripts/analyze_dataset.py \
    --data-dir data \
    --output-dir results \
    --subset-size 100

# Step 2: Convert patient responses to GenAlpha speak
python scripts/convert_to_genalpha.py \
    --input results/evaluation_subset.csv \
    --output results/evaluation_subset_genalpha.csv \
    --intensity 0.7

# Step 3: View some examples
head -20 results/evaluation_subset_genalpha.csv

# Step 4: Run evaluation (requires API keys)
export OPENAI_API_KEY="your-key-here"
python scripts/run_evaluation.py \
    --input results/evaluation_subset_genalpha.csv \
    --output-dir results \
    --model gpt-4 \
    --original-col "patient_original" \
    --genalpha-col "patient_genalpha" \
    --limit 10  # Start small for testing
```

## 3. Check Results

```bash
# View the analysis
cat results/dataset_analysis.json

# View evaluation summary
cat results/evaluation_summary_gpt-4.json
```

## Testing Without Full Dataset

If you want to test the scripts before downloading the full dataset:

```python
# Create a test CSV file
import pandas as pd

test_data = pd.DataFrame({
    'patient': [
        "I've been feeling really anxious about my exams lately.",
        "I don't know how to deal with my anger issues.",
        "I feel like nobody understands me."
    ],
    'therapist': [
        "It sounds like you're experiencing a lot of stress. Can you tell me more?",
        "Let's explore what triggers these feelings of anger.",
        "I hear you. Feeling misunderstood can be very isolating."
    ]
})

test_data.to_csv('data/test_conversations.csv', index=False)
```

Then run the scripts on this test file!

## Common Issues

**Script can't find columns**: Use `--patient-col` and `--therapist-col` to specify column names

**API rate limits**: Add `--limit 10` to test with fewer samples first

**Missing dependencies**: Run `pip install -r requirements.txt`

## What to Expect

After running the pipeline, you'll have:

1. **dataset_analysis.json** - Statistics about your dataset
2. **evaluation_subset.csv** - Representative sample for testing
3. **evaluation_subset_genalpha.csv** - Same conversations with GenAlpha conversions
4. **evaluation_results_{model}.csv** - Detailed comparison of model responses
5. **evaluation_summary_{model}.json** - Aggregate statistics

## Next: Analysis

Check out the example conversions in the GenAlpha dataset:
- Original patient messages
- Converted GenAlpha versions
- How much they differ

This will help you understand if the conversion quality is good before running expensive model evaluations!
