#!/bin/bash
# Start Streamlit frontend

echo "🎨 Starting GenAlpha Therapy Explorer (Streamlit)..."
echo "App will be available at: http://localhost:8501"
echo ""

cd "$(dirname "$0")"
streamlit run streamlit_app.py
