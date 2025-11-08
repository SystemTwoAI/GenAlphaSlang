# Quick Installation Guide

**Having pyarrow errors? Start here!**

## 🚀 Fast Install (2 minutes)

### Step 1: Run the setup script

```bash
./setup.sh
```

Choose **Option 1: Minimal** when prompted.

### Step 2: Test it works

```bash
python scripts/example_using_modules.py
```

You should see:
```
✓ Loaded 50 conversations
✓ Parsed 18 turns
✓ Valid conversation: True
...
```

**Done!** You're ready to use the project.

---

## Manual Install (if script doesn't work)

### Option A: Minimal Install (Recommended)

```bash
# Just 4 packages - no pyarrow issues
pip install pandas numpy python-dotenv tqdm
```

### Option B: With UI

```bash
# Core + Streamlit
pip install pandas numpy python-dotenv tqdm streamlit
```

### Option C: Full Featured

```bash
# Everything
pip install pandas numpy python-dotenv tqdm streamlit anthropic matplotlib
```

---

## Still Having Issues?

### pyarrow errors?

**Solution:** Skip it! Run this:

```bash
pip install pandas numpy python-dotenv tqdm
```

pandas works fine without pyarrow for this project.

### Import errors?

**Solution:** Make sure you're in the project directory:

```bash
cd /path/to/GenAlphaSlang
python scripts/your_script.py
```

### Other issues?

See the full guide: [docs/INSTALLATION.md](docs/INSTALLATION.md)

---

## What You Can Do Now

### 1. Try the Demo

```bash
python scripts/example_using_modules.py
```

### 2. Run an Evaluation

```bash
python scripts/run_multi_turn_evaluation.py single \
    --conversation-id identity_74685 \
    --provider test \
    --max-turns 3
```

### 3. Launch the UI (if you installed streamlit)

```bash
streamlit run app/evaluation_ui.py
```

### 4. Explore the Code

```bash
ls scripts/          # See available scripts
ls docs/            # Read documentation
python -c "from src import utils; help(utils)"  # Explore utilities
```

---

## Next Steps

- Read: [docs/QUICKSTART.md](docs/QUICKSTART.md)
- Read: [docs/MULTI_TURN_EVALUATION_GUIDE.md](docs/MULTI_TURN_EVALUATION_GUIDE.md)
- Check: [docs/CODE_STRUCTURE_ANALYSIS.md](docs/CODE_STRUCTURE_ANALYSIS.md)

---

**Questions?** Check [docs/INSTALLATION.md](docs/INSTALLATION.md) for detailed troubleshooting.

**Author:** Manisha Mehta (manisha.mehta@systemtwoai.com)
