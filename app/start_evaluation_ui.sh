#!/bin/bash
#
# Launch Multi-Turn Evaluation UI
#
# Author: Manisha Mehta (manisha.mehta@systemtwoai.com)

cd "$(dirname "$0")"

echo "=================================="
echo "Multi-Turn Evaluation UI"
echo "=================================="
echo ""
echo "Starting Streamlit interface..."
echo "Access at: http://localhost:8501"
echo ""

streamlit run evaluation_ui.py
