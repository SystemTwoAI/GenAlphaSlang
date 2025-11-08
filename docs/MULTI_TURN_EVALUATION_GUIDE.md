# Multi-Turn Conversation Evaluation Guide

**Author:** Manisha Mehta (manisha.mehta@systemtwoai.com)
**Date:** November 2025

---

## Overview

The Multi-Turn Evaluation Framework allows evaluators (humans or LLMs) to respond to therapy conversations **turn-by-turn**, choosing between:

1. **Free-form responses** - Write your own therapeutic response
2. **Multiple-choice selection** - Select from provided response options

This enables systematic evaluation of how different models or humans handle patient messages across multiple conversational turns.

---

## Use Cases

### 1. **Human Evaluation**
- Mental health professionals evaluate LLM-generated conversations
- Compare therapeutic quality across different response styles
- Assess understanding of GenAlpha language vs standard language

### 2. **LLM Evaluation**
- Automated testing of different models (Claude, GPT-4, etc.)
- Compare responses to original vs GenAlpha patient language
- Benchmark therapeutic conversation abilities

### 3. **Comparative Studies**
- Compare human vs LLM responses on same conversations
- Evaluate consistency across turns
- Analyze response selection patterns

---

## Architecture

```
┌─────────────────────────────────────────────┐
│         Multi-Turn Evaluator                │
├─────────────────────────────────────────────┤
│  ┌───────────────────────────────────────┐ │
│  │  EvaluationTurn                       │ │
│  │  - Patient message                    │ │
│  │  - Conversation history               │ │
│  │  - Response options (optional)        │ │
│  └───────────────────────────────────────┘ │
│                                             │
│  ┌───────────────────────────────────────┐ │
│  │  EvaluatorResponse                    │ │
│  │  - Response text                      │ │
│  │  - Response type (free/choice)        │ │
│  │  - Response time                      │ │
│  └───────────────────────────────────────┘ │
│                                             │
│  ┌───────────────────────────────────────┐ │
│  │  EvaluationSession                    │ │
│  │  - Session ID                         │ │
│  │  - Evaluator info                     │ │
│  │  - All responses                      │ │
│  │  - Progress tracking                  │ │
│  └───────────────────────────────────────┘ │
└─────────────────────────────────────────────┘
```

---

## Quick Start

### Option 1: Interactive UI (Streamlit)

**Launch the evaluation interface:**

```bash
cd app
streamlit run evaluation_ui.py
```

**Steps:**
1. Enter your Evaluator ID (e.g., "evaluator_001" or "GPT-4")
2. Select evaluator type (human, claude, gpt4, etc.)
3. Choose a conversation from a benchmark
4. Select version (Original or GenAlpha)
5. Set number of turns (1-10)
6. Click "Load Conversation"
7. For each turn:
   - Read patient message and conversation history
   - Choose response mode (Write Own or Select from Options)
   - Submit response
8. Complete all turns to finish evaluation

### Option 2: Automated LLM Evaluation

**Single conversation:**

```bash
python scripts/run_multi_turn_evaluation.py single \
    --conversation-id identity_12345 \
    --provider anthropic \
    --model claude-3-5-sonnet-20241022 \
    --max-turns 5
```

**Batch evaluation:**

```bash
python scripts/run_multi_turn_evaluation.py batch \
    --benchmark benchmark_mini_50.csv \
    --num-conversations 10 \
    --provider anthropic \
    --max-turns 5
```

**Analyze results:**

```bash
python scripts/run_multi_turn_evaluation.py analyze
```

---

## Data Structures

### EvaluationTurn

Represents a single turn for evaluation:

```python
{
    "turn_number": 1,
    "patient_message": "I've been feeling really anxious lately...",
    "is_genalpha": false,
    "response_options": [
        {
            "id": "option_1",
            "text": "I understand that must be difficult...",
            "label": "Empathetic Response"
        },
        {
            "id": "option_2",
            "text": "Can you tell me more about what triggers this?",
            "label": "Exploratory Response"
        }
    ],
    "conversation_history": [
        {
            "turn_number": 0,
            "speaker": "patient",
            "text": "I've been feeling really anxious lately..."
        }
    ]
}
```

### EvaluatorResponse

Captures an evaluator's response:

```python
{
    "turn_number": 1,
    "response_type": "free_form",  # or "multiple_choice"
    "response_text": "I hear that you're experiencing anxiety...",
    "selected_option_id": null,  # or option ID if multiple choice
    "timestamp": "2025-11-08T10:30:45",
    "response_time_seconds": 45.3,
    "metadata": {}
}
```

### EvaluationSession

Complete evaluation session:

```python
{
    "session_id": "uuid-here",
    "conversation_id": "identity_12345",
    "evaluator_id": "evaluator_001",
    "evaluator_type": "human",
    "is_genalpha_version": false,
    "max_turns": 5,
    "responses": [...],  # List of EvaluatorResponse
    "started_at": "2025-11-08T10:00:00",
    "completed_at": "2025-11-08T10:15:00",
    "status": "completed"  # or "in_progress", "abandoned"
}
```

---

## Usage Examples

### Example 1: Human Evaluation via UI

```bash
# Launch UI
streamlit run app/evaluation_ui.py

# In browser:
# 1. Enter ID: "therapist_jane"
# 2. Type: "human"
# 3. Select conversation
# 4. Work through 5 turns
# 5. Session auto-saved to results/evaluation_sessions/
```

### Example 2: Compare Claude vs GPT-4

```python
from pathlib import Path
from src.multi_turn_evaluator import EvaluationAnalyzer

# Run evaluations for both models (via CLI or code)
# ...

# Compare results
analyzer = EvaluationAnalyzer(
    Path('results/evaluation_sessions')
)

comparison = analyzer.compare_evaluators(
    conversation_id='identity_12345',
    evaluator_ids=['claude-3-5-sonnet', 'gpt-4']
)

# See turn-by-turn differences
for turn in comparison['turn_comparisons']:
    print(f"Turn {turn['turn_number']}:")
    for evaluator, response in turn['responses'].items():
        print(f"  {evaluator}: {response['response_text'][:100]}")
```

### Example 3: Programmatic Evaluation

```python
import sys
from pathlib import Path
sys.path.insert(0, 'src')

from multi_turn_evaluator import MultiTurnEvaluator
from utils import parse_conversation, load_benchmark

# Setup
evaluator = MultiTurnEvaluator(
    output_dir=Path('results/evaluation_sessions')
)

# Load conversation
df = load_benchmark('benchmark_mini_50.csv')
row = df.iloc[0]
conversation = parse_conversation(row['conversations'])

# Create evaluation turns
eval_turns = evaluator.create_evaluation_turns(
    conversation,
    max_turns=3,
    generate_options=True
)

# Start session
session = evaluator.start_session(
    conversation_id=row['id'],
    evaluator_id='my_evaluator',
    evaluator_type='human',
    evaluation_turns=eval_turns
)

# Submit responses
for turn in eval_turns:
    response_text = input(f"Patient: {turn.patient_message}\nYour response: ")

    evaluator.submit_response(
        turn_number=turn.turn_number,
        response_text=response_text,
        response_type='free_form'
    )

print(f"Evaluation complete! Session: {session.session_id}")
```

---

## Response Options Generation

Currently, response options include:
1. **Original Response** - From the dataset
2. **Alternative Responses** - Placeholder (to be generated)

**Future enhancements:**
- Generate alternatives using different therapeutic approaches
- Vary empathy levels, directiveness, etc.
- Use LLMs to generate diverse options
- Include deliberately poor responses for discrimination testing

---

## Analysis Features

### 1. Overall Statistics

```python
from src.multi_turn_evaluator import EvaluationAnalyzer

analyzer = EvaluationAnalyzer('results/evaluation_sessions')
stats = analyzer.analyze_response_patterns()

# Returns:
{
    "total_sessions": 50,
    "completed_sessions": 45,
    "response_type_distribution": {
        "free_form": 120,
        "multiple_choice": 105
    },
    "avg_response_time": 32.5,
    "completion_rate": 0.90
}
```

### 2. Evaluator Comparison

```python
comparison = analyzer.compare_evaluators(
    conversation_id='identity_12345',
    evaluator_ids=['human_001', 'claude', 'gpt4']
)

# Returns turn-by-turn comparison
```

### 3. Response Pattern Analysis

- Response type preferences
- Average response times
- Completion rates
- Free-form vs multiple-choice usage

---

## File Storage

**Location:** `results/evaluation_sessions/`

**Format:** `session_{session_id}.json`

**Example:**
```json
{
  "session_id": "a1b2c3d4-...",
  "conversation_id": "identity_12345",
  "evaluator_id": "claude-3-5-sonnet",
  "evaluator_type": "claude",
  "responses": [
    {
      "turn_number": 1,
      "response_type": "free_form",
      "response_text": "I hear that you're struggling...",
      "response_time_seconds": 2.3
    }
  ],
  "status": "completed"
}
```

---

## Integration with Existing Tools

### With GenAlpha Converter

```python
from src.genalpha_converter import GenAlphaConverter
from src.multi_turn_evaluator import MultiTurnEvaluator

# Convert patient messages to GenAlpha
converter = GenAlphaConverter(intensity=0.7)

# Create two versions
original_conversation = [...]
genalpha_conversation = [
    {
        'from': msg['from'],
        'value': converter.convert_text(msg['value']) if msg['from'] == 'human' else msg['value']
    }
    for msg in original_conversation
]

# Evaluate both versions
# Compare LLM responses to original vs GenAlpha
```

### With Therapeutic Analyzer

```python
from src.therapeutic_analysis import TherapeuticAnalyzer
from src.multi_turn_evaluator import EvaluationAnalyzer

# Load session
analyzer = EvaluationAnalyzer('results/evaluation_sessions')
session = analyzer.load_session('session_id_here')

# Analyze therapeutic quality of responses
therapeutic_analyzer = TherapeuticAnalyzer()

for response in session.responses:
    metrics = therapeutic_analyzer.analyze_turn(response.response_text)
    print(f"Turn {response.turn_number}:")
    print(f"  Empathy: {metrics['has_empathy']}")
    print(f"  Questions: {metrics['question_counts']}")
```

---

## Best Practices

### For Human Evaluators

1. **Read Full History** - Always review conversation history before responding
2. **Take Your Time** - Quality over speed
3. **Stay In Character** - Respond as a therapist would
4. **Be Consistent** - Maintain similar style across turns
5. **Use Both Modes** - Try both free-form and multiple-choice

### For LLM Evaluations

1. **Set Consistent Temperature** - Use same settings across evaluations
2. **Rate Limiting** - Add delays between requests
3. **Error Handling** - Handle API failures gracefully
4. **Reproducibility** - Set random seeds where possible
5. **Batch Processing** - Evaluate multiple conversations for statistical power

### For Comparative Studies

1. **Same Conversations** - Use identical conversations for fair comparison
2. **Balanced Versions** - Test both original and GenAlpha versions
3. **Multiple Evaluators** - Use multiple humans or model runs
4. **Blind Evaluation** - Hide which version (original/GenAlpha) when possible
5. **Document Settings** - Record all parameters and configurations

---

## Troubleshooting

### Issue: Session not saving

**Solution:** Check that output directory exists and is writable
```python
evaluator.output_dir.mkdir(parents=True, exist_ok=True)
```

### Issue: Can't load session

**Solution:** Verify session ID and file existence
```python
filepath = output_dir / f"session_{session_id}.json"
print(f"Looking for: {filepath}")
print(f"Exists: {filepath.exists()}")
```

### Issue: LLM evaluation failing

**Solution:** Check API key and rate limits
```bash
# Set API key
export ANTHROPIC_API_KEY='your-key-here'

# Test with test provider first
python scripts/run_multi_turn_evaluation.py single \
    --conversation-id identity_12345 \
    --provider test
```

---

## Extending the Framework

### Adding Custom Response Options

```python
from src.multi_turn_evaluator import ResponseOption

custom_options = [
    ResponseOption(
        id="empathetic",
        text="I really understand how difficult this must be for you...",
        label="High Empathy",
        metadata={"style": "empathetic", "directiveness": "low"}
    ),
    ResponseOption(
        id="directive",
        text="Here's what I'd like you to try...",
        label="Directive",
        metadata={"style": "directive", "directiveness": "high"}
    )
]

eval_turn.response_options = custom_options
```

### Custom Analysis

```python
from src.multi_turn_evaluator import EvaluationAnalyzer

class CustomAnalyzer(EvaluationAnalyzer):
    def analyze_empathy_trends(self):
        """Analyze how empathy changes across turns."""
        sessions = self.load_all_sessions()

        for session in sessions:
            empathy_scores = []
            for response in session.responses:
                # Custom empathy scoring logic
                score = self.score_empathy(response.response_text)
                empathy_scores.append(score)

            # Analyze trends
            # ...
```

---

## Future Enhancements

1. **Advanced Response Generation**
   - LLM-generated diverse response options
   - Therapeutic approach variations (CBT, DBT, Person-Centered)

2. **Richer Analysis**
   - Therapeutic alliance tracking
   - Emotion detection across turns
   - Conversation coherence metrics

3. **UI Improvements**
   - Real-time comparison mode
   - Response rating system
   - Conversation branching visualization

4. **Integration**
   - Export to research formats
   - Integration with annotation tools
   - API for programmatic access

---

## Citation

If using this framework in research:

```bibtex
@software{genalpha_multi_turn_evaluator,
  author = {Mehta, Manisha},
  title = {Multi-Turn Therapy Conversation Evaluation Framework},
  year = {2025},
  url = {https://github.com/SystemTwoAI/GenAlphaSlang}
}
```

---

**Author:** Manisha Mehta (manisha.mehta@systemtwoai.com)
**Project:** GenAlpha Therapy Conversation Evaluation
**License:** [Your License]
