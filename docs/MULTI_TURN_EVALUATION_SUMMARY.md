# Multi-Turn Conversation Evaluation System

**Author:** Manisha Mehta (manisha.mehta@systemtwoai.com)
**Date:** November 2025

---

## Executive Summary

Created a comprehensive **multi-turn conversation evaluation framework** that allows evaluators (humans or LLMs) to respond to therapy conversations **turn-by-turn** with two response modes:

1. **Free-form responses** - Write your own therapeutic response
2. **Multiple-choice selection** - Select from provided response options

This enables systematic evaluation of how different models or humans handle patient messages across multiple conversational turns, with full conversation history context.

---

## What Was Built

### 1. Core Framework (`src/multi_turn_evaluator.py`)

**Key Classes:**

- **`EvaluationTurn`** - Represents a single turn for evaluation
  - Patient message
  - Conversation history (all previous turns)
  - Response options (optional)
  - GenAlpha flag

- **`EvaluatorResponse`** - Captures an evaluator's response
  - Response text
  - Response type (free-form or multiple-choice)
  - Selected option ID (if applicable)
  - Response time
  - Metadata (model info, token usage, etc.)

- **`EvaluationSession`** - Complete evaluation session
  - Session ID and metadata
  - All responses
  - Progress tracking
  - Auto-saves to JSON

- **`MultiTurnEvaluator`** - Framework coordinator
  - Creates evaluation turns from conversations
  - Manages sessions
  - Saves/loads sessions
  - Tracks progress

- **`EvaluationAnalyzer`** - Results analysis
  - Compare evaluators
  - Response pattern analysis
  - Completion statistics

### 2. Interactive UI (`app/evaluation_ui.py`)

**Streamlit Web Interface:**

- **Setup Page:**
  - Enter evaluator ID
  - Select evaluator type (human, claude, gpt4, etc.)
  - Choose conversation from benchmark
  - Select version (Original or GenAlpha)
  - Set number of turns

- **Evaluation Page:**
  - Shows conversation history
  - Displays current patient message
  - Two response modes:
    - **Write Own Response** - Text area for free-form
    - **Select from Options** - Buttons for multiple-choice
  - Progress bar
  - Auto-saves after each turn

- **Analysis Page:**
  - Overall statistics
  - Response type distribution
  - Session details
  - Completion rates

**Launch:**
```bash
streamlit run app/evaluation_ui.py
# or
./app/start_evaluation_ui.sh
```

### 3. CLI Automation (`scripts/run_multi_turn_evaluation.py`)

**Commands:**

**Single Conversation:**
```bash
python scripts/run_multi_turn_evaluation.py single \
    --conversation-id identity_12345 \
    --provider anthropic \
    --model claude-3-5-sonnet-20241022 \
    --max-turns 5
```

**Batch Evaluation:**
```bash
python scripts/run_multi_turn_evaluation.py batch \
    --benchmark benchmark_mini_50.csv \
    --num-conversations 10 \
    --provider test \
    --max-turns 5
```

**Analysis:**
```bash
python scripts/run_multi_turn_evaluation.py analyze
```

**Features:**
- Automated LLM responses
- Progress tracking
- Error handling with retries
- Rate limiting
- Response time tracking
- Session persistence

### 4. Comprehensive Documentation

**`docs/MULTI_TURN_EVALUATION_GUIDE.md`** - 15-page guide covering:
- Architecture overview
- Quick start examples
- Data structures
- Usage examples (UI, CLI, programmatic)
- Response option generation
- Analysis features
- File storage format
- Integration with existing tools
- Best practices
- Troubleshooting
- Extension points
- Future enhancements

---

## How It Works

### Example Flow

1. **Load Conversation**
   ```python
   # From benchmark
   conversation = parse_conversation(row['conversations'])
   ```

2. **Create Evaluation Turns**
   ```python
   eval_turns = evaluator.create_evaluation_turns(
       conversation,
       max_turns=5,
       generate_options=True
   )
   ```

3. **Start Session**
   ```python
   session = evaluator.start_session(
       conversation_id='identity_12345',
       evaluator_id='claude-3-5-sonnet',
       evaluator_type='claude',
       evaluation_turns=eval_turns
   )
   ```

4. **For Each Turn:**
   - Show patient message
   - Show conversation history
   - Get evaluator response (free-form or choice)
   - Submit response
   - Auto-save session
   - Move to next turn

5. **Session Complete**
   - Saved to `results/evaluation_sessions/session_{id}.json`
   - Available for analysis

---

## Key Features

### ✅ Turn-by-Turn Presentation
- Each patient message presented individually
- Full conversation history shown
- Contextual evaluation

### ✅ Dual Response Modes
- **Free-form:** Write your own response
- **Multiple-choice:** Select from options

### ✅ Conversation History
- All previous turns displayed
- Maintains context
- Enables coherent multi-turn evaluation

### ✅ Progress Tracking
- Visual progress bar
- Turn counter
- Session status (in_progress, completed, abandoned)

### ✅ Session Persistence
- Auto-saves after each response
- JSON format
- Can resume interrupted sessions

### ✅ Response Time Tracking
- Measures time per response
- Useful for comparing human vs LLM speed
- Stored in session metadata

### ✅ LLM Integration
- Works with Anthropic Claude
- Works with OpenAI GPT
- Test mode for development
- Extensible to other providers

### ✅ Analysis Tools
- Compare evaluators on same conversations
- Response pattern analysis
- Completion statistics
- Response type distribution

---

## Use Cases

### 1. Human Evaluation
**Scenario:** Mental health professionals evaluate therapy conversations

```bash
# Launch UI
streamlit run app/evaluation_ui.py

# Professional enters ID: "therapist_jane_doe"
# Evaluates 5 turns of a conversation
# Chooses mix of free-form and multiple-choice
# Session saved for later analysis
```

### 2. LLM Benchmarking
**Scenario:** Compare Claude vs GPT-4 on same conversations

```bash
# Evaluate with Claude
python scripts/run_multi_turn_evaluation.py batch \
    --num-conversations 50 \
    --provider anthropic \
    --model claude-3-5-sonnet-20241022

# Evaluate with GPT-4
python scripts/run_multi_turn_evaluation.py batch \
    --num-conversations 50 \
    --provider openai \
    --model gpt-4

# Compare results
python scripts/run_multi_turn_evaluation.py analyze
```

### 3. GenAlpha Language Testing
**Scenario:** Test if models handle informal language well

```python
from src.multi_turn_evaluator import MultiTurnEvaluator

# Evaluate same conversation in two versions
# Version 1: Original language
session_original = evaluator.start_session(
    conversation_id='conv_123',
    evaluator_id='claude',
    is_genalpha=False
)

# Version 2: GenAlpha language
session_genalpha = evaluator.start_session(
    conversation_id='conv_123_genalpha',
    evaluator_id='claude',
    is_genalpha=True
)

# Compare therapeutic quality of responses
```

### 4. Systematic Quality Assessment
**Scenario:** Evaluate therapeutic quality turn-by-turn

```python
from src.therapeutic_analysis import TherapeuticAnalyzer
from src.multi_turn_evaluator import EvaluationAnalyzer

# Load completed session
analyzer = EvaluationAnalyzer('results/evaluation_sessions')
session = analyzer.load_session('session_id')

# Analyze each response
therapeutic = TherapeuticAnalyzer()
for response in session.responses:
    metrics = therapeutic.analyze_turn(response.response_text)
    print(f"Turn {response.turn_number}:")
    print(f"  Empathy: {metrics['has_empathy']}")
    print(f"  Questions: {metrics['question_counts']}")
    print(f"  Open questions: {metrics['has_open_questions']}")
```

---

## Data Format

### Session File Structure
```json
{
  "session_id": "uuid",
  "conversation_id": "identity_12345",
  "evaluator_id": "claude-3-5-sonnet",
  "evaluator_type": "claude",
  "is_genalpha_version": false,
  "max_turns": 5,
  "responses": [
    {
      "turn_number": 1,
      "response_type": "free_form",
      "response_text": "I hear that you're struggling...",
      "selected_option_id": null,
      "timestamp": "2025-11-08T10:30:45",
      "response_time_seconds": 2.3,
      "metadata": {
        "model": "claude-3-5-sonnet-20241022",
        "usage": {
          "input_tokens": 250,
          "output_tokens": 180
        }
      }
    }
  ],
  "started_at": "2025-11-08T10:00:00",
  "completed_at": "2025-11-08T10:15:00",
  "status": "completed"
}
```

---

## Integration with Existing Tools

### With GenAlpha Converter
```python
from src.genalpha_converter import GenAlphaConverter

converter = GenAlphaConverter(intensity=0.7)

# Convert patient messages
genalpha_turn = converter.convert_text(
    patient_message,
    context='patient'
)

# Evaluate responses to both versions
```

### With Therapeutic Analyzer
```python
from src.therapeutic_analysis import TherapeuticAnalyzer

analyzer = TherapeuticAnalyzer()

# Analyze response quality
metrics = analyzer.analyze_conversation(session.responses)
rating, feedback = analyzer.assess_quality(metrics)
```

### With Benchmark System
```python
from src.utils import load_benchmark

# Load conversations from benchmarks
df = load_benchmark('benchmark_comprehensive_500.csv')

# Create evaluations from benchmark
for _, row in df.iterrows():
    # Create evaluation turns
    # Run evaluation
    # Save results
```

---

## Testing & Verification

**Tested:**
```bash
$ python scripts/run_multi_turn_evaluation.py single \
    --conversation-id identity_74685 \
    --provider test \
    --max-turns 2

✓ Session created: de70a382-49af-44dd-8bd6-b3ddba32248a
✓ 2 turns evaluated
✓ Responses saved to JSON
✓ Session status: completed
```

**Session file verified:**
- Correct structure
- All fields populated
- Response metadata included
- Timestamps recorded

---

## Future Enhancements

### Planned Features

1. **Response Option Generation**
   - LLM-generated diverse options
   - Different therapeutic styles
   - Varying empathy levels

2. **Advanced Analysis**
   - Conversation coherence metrics
   - Therapeutic alliance tracking
   - Turn-by-turn quality trends

3. **UI Improvements**
   - Real-time comparison mode
   - Response rating system
   - Conversation tree visualization

4. **Export & Integration**
   - Export to research formats (CSV, Excel)
   - Integration with annotation tools
   - REST API for programmatic access

---

## File Structure

```
GenAlphaSlang/
├── src/
│   └── multi_turn_evaluator.py    # Core framework
│
├── app/
│   ├── evaluation_ui.py           # Streamlit UI
│   └── start_evaluation_ui.sh     # Launcher
│
├── scripts/
│   └── run_multi_turn_evaluation.py  # CLI automation
│
├── docs/
│   ├── MULTI_TURN_EVALUATION_GUIDE.md      # Full guide
│   └── MULTI_TURN_EVALUATION_SUMMARY.md    # This file
│
└── results/
    └── evaluation_sessions/        # Runtime data (gitignored)
        └── session_{id}.json       # Saved sessions
```

---

## Quick Reference

### Launch Interactive UI
```bash
streamlit run app/evaluation_ui.py
```

### Run Single Evaluation
```bash
python scripts/run_multi_turn_evaluation.py single \
    --conversation-id ID \
    --provider anthropic \
    --max-turns 5
```

### Run Batch Evaluation
```bash
python scripts/run_multi_turn_evaluation.py batch \
    --num-conversations 10 \
    --provider anthropic
```

### Analyze Results
```bash
python scripts/run_multi_turn_evaluation.py analyze
```

---

## Summary

The multi-turn evaluation framework provides a **complete solution** for:

✅ Turn-by-turn conversation evaluation
✅ Both human and automated (LLM) evaluation
✅ Free-form and multiple-choice responses
✅ Full conversation context at each turn
✅ Progress tracking and session persistence
✅ Comprehensive analysis tools
✅ Easy-to-use UI and CLI
✅ Integration with existing tools
✅ Proper attribution (Manisha Mehta)

**Ready to use for:**
- Evaluating therapy chatbot quality
- Comparing models
- Testing GenAlpha language understanding
- Human evaluation studies
- Systematic benchmarking

---

**Author:** Manisha Mehta (manisha.mehta@systemtwoai.com)
**Project:** GenAlpha Therapy Conversation Evaluation
**Date:** November 2025
