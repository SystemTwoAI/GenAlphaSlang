# Installation Guide

**Author:** Manisha Mehta (manisha.mehta@systemtwoai.com)
**Date:** November 2025

---

## Quick Start (Recommended)

### Option 1: Minimal Install (No pyarrow issues)

```bash
# Install only core dependencies
pip install pandas numpy python-dotenv tqdm
```

This installs the minimal set needed to run most scripts. It avoids pyarrow entirely.

---

## Troubleshooting pyarrow Errors

If you encounter errors like:
```
ERROR: Could not build wheels for pyarrow
ERROR: Failed building wheel for pyarrow
```

Try one of these solutions:

### Solution 1: Skip Optional Dependencies

```bash
# Install core packages only
pip install pandas numpy python-dotenv tqdm

# Then add what you need:
pip install streamlit  # If you want the UI
pip install anthropic  # If you want Claude API
```

### Solution 2: Use requirements-minimal.txt

```bash
pip install -r requirements-minimal.txt
```

### Solution 3: Install pandas without binaries

```bash
# This compiles from source and avoids binary compatibility issues
pip install --no-binary :all: pandas numpy
pip install python-dotenv tqdm
```

### Solution 4: Install specific pyarrow version

```bash
# Try different pyarrow versions
pip install pyarrow==14.0.1
pip install pandas numpy

# Or try the latest
pip install pyarrow
pip install pandas numpy
```

### Solution 5: Upgrade pip and setuptools

```bash
# Update installation tools
pip install --upgrade pip setuptools wheel

# Then try installing
pip install pandas numpy
```

### Solution 6: Use Conda (if you have it)

```bash
conda install pandas numpy
conda install -c conda-forge python-dotenv tqdm
```

---

## Full Installation (All Features)

Once you've resolved pyarrow issues, install additional features:

### For Interactive UI (Streamlit)

```bash
pip install streamlit fastapi uvicorn requests
```

### For LLM APIs

```bash
# For Claude
pip install anthropic

# For OpenAI
pip install openai
```

### For Data Analysis & Visualization

```bash
pip install matplotlib seaborn jupyter
```

---

## Platform-Specific Issues

### macOS (M1/M2 Apple Silicon)

```bash
# Use conda for better compatibility
conda create -n genalpha python=3.11
conda activate genalpha
conda install pandas numpy
pip install python-dotenv tqdm streamlit
```

Or:

```bash
# Install Rosetta 2 version of Python
arch -x86_64 python3 -m pip install pandas numpy
```

### Windows

```bash
# Make sure you have Visual C++ Build Tools installed
# Download from: https://visualstudio.microsoft.com/downloads/

# Then install
pip install pandas numpy python-dotenv tqdm
```

### Linux

```bash
# Install build dependencies first
sudo apt-get update
sudo apt-get install -y python3-dev build-essential

# Then install packages
pip install pandas numpy python-dotenv tqdm
```

---

## Verify Installation

Test if everything works:

```bash
# Test basic imports
python -c "import pandas; import numpy; print('✓ Core libraries working')"

# Test project utilities
python -c "from src.utils import parse_conversation; print('✓ Project utilities working')"

# Test with a script
python scripts/example_using_modules.py
```

---

## Environment Setup

### Create Virtual Environment (Recommended)

```bash
# Create virtual environment
python -m venv venv

# Activate it
# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements-minimal.txt
```

### Using .env for API Keys

```bash
# Create .env file
cp .env.example .env  # If example exists

# Or create manually:
cat > .env << 'EOF'
ANTHROPIC_API_KEY=your_key_here
OPENAI_API_KEY=your_key_here
EOF
```

---

## Dependency Details

### Required (Core Functionality)

| Package | Version | Purpose |
|---------|---------|---------|
| pandas | >=2.0.0,<2.2.0 | Data handling |
| numpy | >=1.24.0,<2.0.0 | Numerical operations |
| python-dotenv | >=1.0.0 | Environment variables |
| tqdm | >=4.65.0 | Progress bars |

### Optional (Streamlit UI)

| Package | Version | Purpose |
|---------|---------|---------|
| streamlit | >=1.28.0,<2.0.0 | Web UI framework |
| fastapi | >=0.104.0,<1.0.0 | API backend |
| uvicorn | >=0.24.0,<1.0.0 | ASGI server |
| requests | >=2.31.0 | HTTP requests |

### Optional (LLM APIs)

| Package | Version | Purpose |
|---------|---------|---------|
| anthropic | >=0.25.0 | Claude API |
| openai | >=1.0.0 | GPT-4 API |

### Optional (Analysis & Visualization)

| Package | Version | Purpose |
|---------|---------|---------|
| matplotlib | >=3.7.0,<4.0.0 | Plotting |
| seaborn | >=0.12.0,<0.14.0 | Statistical viz |
| jupyter | >=1.0.0 | Notebooks |

---

## What Works Without pyarrow?

**Everything!** pyarrow is an optional dependency for pandas that provides:
- Faster reading/writing of Parquet files
- Better memory efficiency for some operations

Since we're using CSV files, **pyarrow is not needed** for this project.

---

## Testing Your Installation

### Test 1: Core Utilities

```bash
python scripts/example_using_modules.py
```

Expected output:
```
✓ Loaded 50 conversations
✓ Parsed 18 turns
✓ Valid conversation: True
...
```

### Test 2: Analysis Scripts

```bash
python scripts/analyze_realism.py
```

Should run without errors.

### Test 3: Multi-Turn Evaluation

```bash
python scripts/run_multi_turn_evaluation.py single \
    --conversation-id identity_74685 \
    --provider test \
    --max-turns 2
```

Should complete successfully.

### Test 4: Streamlit UI (if installed)

```bash
streamlit run app/evaluation_ui.py
```

Should launch browser at http://localhost:8501

---

## Common Errors & Solutions

### Error: "No module named 'src'"

**Solution:** Run scripts from the project root directory:
```bash
cd /path/to/GenAlphaSlang
python scripts/your_script.py
```

### Error: "FileNotFoundError: Benchmark not found"

**Solution:** Make sure you're in the project root:
```bash
pwd  # Should show .../GenAlphaSlang
ls results/  # Should show benchmark files
```

### Error: "ImportError: No module named 'pandas'"

**Solution:** Install dependencies:
```bash
pip install pandas numpy
```

### Error: "ModuleNotFoundError: No module named 'streamlit'"

**Solution:** Streamlit is optional. Install if needed:
```bash
pip install streamlit
```

### Error: "API key not found"

**Solution:** Set environment variable:
```bash
export ANTHROPIC_API_KEY='your-key-here'
```

Or create .env file:
```bash
echo "ANTHROPIC_API_KEY=your-key-here" > .env
```

---

## Recommended Installation Path

For most users, we recommend:

```bash
# 1. Create virtual environment
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# 2. Update pip
pip install --upgrade pip

# 3. Install minimal dependencies
pip install pandas numpy python-dotenv tqdm

# 4. Test it works
python scripts/example_using_modules.py

# 5. Add optional features as needed
pip install streamlit  # For UI
pip install anthropic  # For Claude API
```

---

## Getting Help

If you continue to have installation issues:

1. **Check Python version:** `python --version` (should be 3.8+)
2. **Check pip version:** `pip --version`
3. **Try minimal install:** `pip install -r requirements-minimal.txt`
4. **Create fresh virtual environment**
5. **Check system requirements:**
   - macOS: Xcode Command Line Tools
   - Windows: Visual C++ Build Tools
   - Linux: build-essential, python3-dev

---

## Next Steps

After installation:

1. **Explore the data:**
   ```bash
   python scripts/example_using_modules.py
   ```

2. **Try the interactive UI:**
   ```bash
   streamlit run app/evaluation_ui.py
   ```

3. **Run an evaluation:**
   ```bash
   python scripts/run_multi_turn_evaluation.py single \
       --conversation-id identity_74685 \
       --provider test
   ```

4. **Read the docs:**
   - `docs/QUICKSTART.md`
   - `docs/MULTI_TURN_EVALUATION_GUIDE.md`
   - `docs/CODE_STRUCTURE_ANALYSIS.md`

---

**Author:** Manisha Mehta (manisha.mehta@systemtwoai.com)
**Project:** GenAlpha Therapy Conversation Evaluation
