#!/bin/bash
#
# Quick setup script for GenAlpha Therapy Conversation Evaluation
#
# Author: Manisha Mehta (manisha.mehta@systemtwoai.com)

set -e  # Exit on error

echo "=============================================="
echo "GenAlpha Therapy Dataset - Quick Setup"
echo "=============================================="
echo ""
echo "Author: Manisha Mehta (manisha.mehta@systemtwoai.com)"
echo ""

# Check Python version
echo "Checking Python version..."
python_version=$(python --version 2>&1 | awk '{print $2}')
echo "Found Python $python_version"

# Detect platform
if [[ "$OSTYPE" == "darwin"* ]]; then
    platform="macOS"
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    platform="Linux"
elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
    platform="Windows"
else
    platform="Unknown"
fi

echo "Platform: $platform"
echo ""

# Upgrade pip
echo "Upgrading pip..."
python -m pip install --upgrade pip --quiet

# Offer installation options
echo "=============================================="
echo "Installation Options"
echo "=============================================="
echo ""
echo "1. Minimal (Core only - no pyarrow issues)"
echo "2. Full (All features - may have pyarrow issues)"
echo "3. Custom (Choose what to install)"
echo ""
read -p "Select option (1-3): " choice

case $choice in
    1)
        echo ""
        echo "Installing minimal dependencies..."
        pip install pandas numpy python-dotenv tqdm
        echo ""
        echo "✓ Minimal installation complete!"
        ;;
    2)
        echo ""
        echo "Installing full dependencies..."
        echo "(This may take a few minutes and might encounter pyarrow issues)"
        pip install -r requirements.txt || {
            echo ""
            echo "⚠️  Full installation encountered errors."
            echo "Falling back to minimal installation..."
            pip install pandas numpy python-dotenv tqdm
            echo ""
            echo "✓ Minimal installation complete!"
            echo "  See docs/INSTALLATION.md for troubleshooting"
        }
        ;;
    3)
        echo ""
        echo "Custom installation:"
        echo ""

        # Core
        echo "Installing core dependencies..."
        pip install pandas numpy python-dotenv tqdm

        # Ask about UI
        read -p "Install Streamlit UI? (y/n): " install_ui
        if [[ $install_ui == "y" ]]; then
            echo "Installing Streamlit..."
            pip install streamlit fastapi uvicorn requests
        fi

        # Ask about LLM APIs
        read -p "Install LLM APIs (Claude, GPT-4)? (y/n): " install_llm
        if [[ $install_llm == "y" ]]; then
            echo "Installing LLM API clients..."
            pip install anthropic openai
        fi

        # Ask about visualization
        read -p "Install visualization tools? (y/n): " install_viz
        if [[ $install_viz == "y" ]]; then
            echo "Installing visualization tools..."
            pip install matplotlib seaborn
        fi

        echo ""
        echo "✓ Custom installation complete!"
        ;;
    *)
        echo "Invalid option. Exiting."
        exit 1
        ;;
esac

# Verify installation
echo ""
echo "=============================================="
echo "Verifying Installation"
echo "=============================================="
echo ""

python -c "import pandas; import numpy; print('✓ Core libraries working')" || {
    echo "✗ Core libraries failed to import"
    exit 1
}

python -c "from src.utils import parse_conversation; print('✓ Project utilities working')" || {
    echo "✗ Project utilities failed to import"
    exit 1
}

# Test a script
echo "Running test script..."
python scripts/example_using_modules.py > /dev/null 2>&1 && echo "✓ Test script successful" || echo "⚠️  Test script had issues (may be okay)"

echo ""
echo "=============================================="
echo "Setup Complete!"
echo "=============================================="
echo ""
echo "Next steps:"
echo ""
echo "  1. Try the example:"
echo "     python scripts/example_using_modules.py"
echo ""
echo "  2. Launch the UI (if installed):"
echo "     streamlit run app/evaluation_ui.py"
echo ""
echo "  3. Run an evaluation:"
echo "     python scripts/run_multi_turn_evaluation.py single \\"
echo "       --conversation-id identity_74685 --provider test"
echo ""
echo "  4. Read the docs:"
echo "     docs/INSTALLATION.md"
echo "     docs/QUICKSTART.md"
echo "     docs/MULTI_TURN_EVALUATION_GUIDE.md"
echo ""
echo "For troubleshooting, see: docs/INSTALLATION.md"
echo ""
