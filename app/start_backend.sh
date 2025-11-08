#!/bin/bash
# Start FastAPI backend server

echo "🚀 Starting GenAlpha Therapy API Backend..."
echo "API will be available at: http://localhost:8000"
echo "API Docs will be available at: http://localhost:8000/docs"
echo ""

cd "$(dirname "$0")"
python -m uvicorn backend:app --reload --host 0.0.0.0 --port 8000
