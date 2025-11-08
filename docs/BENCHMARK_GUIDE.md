# GenAlpha Therapy Benchmark Guide

This guide explains the benchmark datasets created from the synthetic therapy conversations for evaluating GenAlpha language conversion quality.

## Dataset Quality Assessment

### Overall Statistics
- **Total Conversations**: 99,086
- **Average Turns per Conversation**: 16.2 (median: 16)
- **Range**: 2 to 190 turns
- **Complete Conversations**: 93.5% (have both opening and closing exchanges)
- **Therapeutic Language Present**: 93.6%

### Conversation Characteristics

**Turn Distribution:**
- 25th percentile: 14 turns
- 50th percentile (median): 16 turns
- 75th percentile: 18 turns
- 90th percentile: 20 turns

**Message Lengths:**
- Average patient message: 230 characters
- Average therapist message: 271 characters

**Quality Indicators:**
- Empathy markers per therapist turn: 0.91
- Emotion words per patient turn: 0.93

### Topic Distribution (from 2,000-conversation sample)

| Topic | Percentage |
|-------|-----------|
| Depression | 59.9% |
| Work Stress | 54.4% |
| Anxiety | 51.5% |
| Health | 48.4% |
| Relationships | 41.2% |
| Family | 27.8% |
| Self-Esteem | 24.2% |
| Addiction | 21.7% |
| Grief | 8.5% |
| Trauma | 3.8% |

*Note: Topics overlap; one conversation may cover multiple topics*

### Complexity Distribution

| Complexity | Definition | Percentage | Use Case |
|-----------|-----------|------------|----------|
| **Simple** | 2-6 turns | 0.4% | Quick exchanges, basic clarification |
| **Moderate** | 7-15 turns | 33.1% | Exploratory conversations, initial sessions |
| **Complex** | 16+ turns | 60.0% | Deep therapeutic work, multi-issue sessions |

**Key Finding**: Dataset is heavily skewed toward complex, multi-turn therapeutic conversations (60%), making it ideal for evaluating sustained dialogue quality.

## Benchmark Datasets

We've created 4 benchmark subsets for different evaluation needs:

### 1. Mini Benchmark (50 conversations)
**File:** `benchmark_mini_50.csv`
**Size:** 234 KB

**Purpose:**
- Quick smoke testing during development
- Rapid iteration on GenAlpha conversion parameters
- Fast validation of changes

**Use When:**
- Testing new conversion rules
- Debugging GenAlpha converter
- Quick sanity checks

**Command:**
```bash
python scripts/process_therapy_dataset.py \
    --input results/benchmark_mini_50.csv \
    --output results/mini_genalpha.csv \
    --intensity 0.7
```

### 2. Standard Benchmark (200 conversations)
**File:** `benchmark_standard_200.csv`
**Size:** 901 KB

**Purpose:**
- Regular evaluation during development
- Standard model testing
- Comparison across different approaches

**Use When:**
- Evaluating model responses
- Comparing conversion intensities
- Standard quality checks

**Expected Runtime:** ~10-20 minutes with API calls

### 3. Comprehensive Benchmark (500 conversations)
**File:** `benchmark_comprehensive_500.csv`
**Size:** 2.2 MB

**Purpose:**
- Thorough evaluation for research
- Publication-quality results
- Detecting subtle differences

**Use When:**
- Final evaluation for papers
- Comprehensive model comparison
- Statistical significance testing

**Expected Runtime:** ~30-60 minutes with API calls

### 4. Stratified Benchmark (300 conversations)
**File:** `benchmark_stratified_300.csv`
**Size:** 959 KB

**Purpose:**
- Balanced evaluation across complexity levels
- Testing performance on different conversation types
- Ensuring coverage of edge cases

**Composition:**
- 100 simple conversations (2-6 turns)
- 100 moderate conversations (7-15 turns)
- 100 complex conversations (16+ turns)

**Use When:**
- Need balanced representation
- Testing across difficulty levels
- Comprehensive coverage needed

**Key Benefit:** Ensures GenAlpha conversion works well for both quick exchanges and deep therapeutic sessions.

## Recommended Evaluation Pipeline

### Phase 1: Development (Mini Benchmark)
```bash
# 1. Test conversion
python scripts/process_therapy_dataset.py \
    --input results/benchmark_mini_50.csv \
    --output results/mini_genalpha.csv

# 2. Quick visual inspection
head -100 results/mini_genalpha.csv
```

### Phase 2: Validation (Standard Benchmark)
```bash
# 1. Convert with chosen intensity
python scripts/process_therapy_dataset.py \
    --input results/benchmark_standard_200.csv \
    --output results/standard_genalpha.csv \
    --intensity 0.7

# 2. Run model evaluation (if API configured)
python scripts/run_evaluation.py \
    --input results/standard_genalpha.csv \
    --model gpt-4 \
    --limit 50
```

### Phase 3: Research Evaluation (Comprehensive or Stratified)
```bash
# Option A: Comprehensive
python scripts/process_therapy_dataset.py \
    --input results/benchmark_comprehensive_500.csv \
    --output results/comprehensive_genalpha.csv

# Option B: Stratified (recommended for balanced evaluation)
python scripts/process_therapy_dataset.py \
    --input results/benchmark_stratified_300.csv \
    --output results/stratified_genalpha.csv

# Run full evaluation
python scripts/run_evaluation.py \
    --input results/stratified_genalpha.csv \
    --model gpt-4 \
    --original-col "first_patient_original" \
    --genalpha-col "first_patient_genalpha"
```

## Benchmark Selection Guide

| Scenario | Recommended Benchmark | Reason |
|----------|---------------------|---------|
| Testing new conversion rule | Mini (50) | Fast iteration |
| Comparing 2-3 approaches | Standard (200) | Good balance |
| Publication/research | Comprehensive (500) | Statistical power |
| Need balanced coverage | Stratified (300) | All complexity levels |
| Limited API budget | Mini or Standard | Fewer API calls |
| Checking edge cases | Stratified (300) | Includes rare simple cases |

## Quality Assurance

### Before Using Benchmarks

1. **Verify conversion quality on Mini benchmark first**
2. **Check examples manually** - spot check 5-10 conversions
3. **Validate intensity setting** - too high can corrupt meaning
4. **Test on Standard before Comprehensive** - saves time and cost

### Expected Conversion Characteristics

Based on our evaluation subset results:

**What Should Happen:**
- ✅ Core therapeutic meaning preserved
- ✅ Emotion words maintained/adapted ("sad" → "in my feels")
- ✅ Slang naturally integrated ("really" → "fr", "I don't know" → "idk")
- ✅ Sentence structure adapted but readable

**Red Flags:**
- ❌ Complete meaning change
- ❌ Loss of emotional content
- ❌ Excessive slang that obscures meaning
- ❌ Therapist responses modified (should stay unchanged)

## Benchmark Statistics

| Benchmark | Conversations | Avg Turns | Size | Est. API Calls* |
|-----------|--------------|-----------|------|----------------|
| Mini | 50 | ~16 | 234 KB | 100 |
| Standard | 200 | ~16 | 901 KB | 400 |
| Comprehensive | 500 | ~16 | 2.2 MB | 1,000 |
| Stratified | 300 | ~16 | 959 KB | 600 |

*Estimated API calls = conversations × 2 (original + GenAlpha)

## Reproducing Benchmarks

To recreate benchmarks with different parameters:

```bash
# Run the analysis again with custom settings
python scripts/analyze_quality_and_benchmark.py \
    --data-file data/chunks/train.csv \
    --output-dir results \
    --sample-size 3000

# This will regenerate:
# - All 4 benchmark files
# - Quality analysis JSON
# - Topic distribution
```

## Next Steps

1. **Start with Mini benchmark** to validate your setup
2. **Use Standard for development** and parameter tuning
3. **Use Stratified for comprehensive testing** to ensure quality across all complexity levels
4. **Use Comprehensive for final evaluation** and publication

## Files Generated

```
results/
├── benchmark_mini_50.csv           # Quick testing
├── benchmark_standard_200.csv       # Regular evaluation
├── benchmark_comprehensive_500.csv  # Thorough analysis
├── benchmark_stratified_300.csv     # Balanced coverage
└── dataset_quality_analysis.json    # Full quality report
```

## Citation

When using these benchmarks in research:

```
Synthetic Therapy Conversations Dataset with GenAlpha Conversion
- Source: Kaggle (thedevastator/synthetic-therapy-conversations-dataset)
- Total: 99,086 conversations
- Benchmark Subsets: 50/200/300/500 conversations
- Stratification: By conversation complexity (turns)
- Topics: Depression, Anxiety, Relationships, Work Stress, etc.
```

## Support

For issues or questions:
- Check `DATA_CHUNKING.md` for dataset assembly
- See `CONVERSION_EXAMPLES.md` for GenAlpha conversion examples
- Review `README.md` for overall project documentation
