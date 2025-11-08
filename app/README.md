# GenAlpha Therapy Explorer

Interactive web application for exploring therapy conversations and GenAlpha language conversions.

## Components

### 1. Streamlit Frontend (`streamlit_app.py`)
Interactive UI for browsing and converting conversations.

**Features:**
- Browse therapy conversations from multiple benchmarks
- Real-time GenAlpha conversion with adjustable intensity
- Side-by-side comparison of original vs GenAlpha
- Custom text conversion tool
- Statistics and visualizations
- Built-in documentation

### 2. FastAPI Backend (`backend.py`) [Optional]
REST API for serving conversation data and conversions.

**Endpoints:**
- `GET /` - API info
- `GET /benchmarks` - List available benchmarks
- `GET /conversations/{benchmark}` - Get all conversations
- `GET /conversation/{benchmark}/{index}` - Get specific conversation
- `POST /convert` - Convert text to GenAlpha
- `POST /convert_conversation` - Convert full conversation
- `GET /stats/{benchmark}` - Get benchmark statistics
- `GET /health` - Health check

## Quick Start

### Option 1: Streamlit Only (Recommended)

The Streamlit app works standalone without the FastAPI backend:

```bash
# Install dependencies
pip install -r requirements.txt

# Start Streamlit
./start_streamlit.sh

# Or manually:
streamlit run streamlit_app.py
```

Access at: http://localhost:8501

### Option 2: With FastAPI Backend

For API access or multi-user scenarios:

```bash
# Terminal 1: Start backend
./start_backend.sh
# Or: python -m uvicorn backend:app --reload

# Terminal 2: Start frontend
./start_streamlit.sh
```

**Access:**
- Frontend: http://localhost:8501
- API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## Installation

### From Root Directory

```bash
cd app
pip install -r requirements.txt
```

### Dependencies

- **streamlit**: Interactive web UI
- **fastapi**: REST API framework (optional)
- **uvicorn**: ASGI server for FastAPI (optional)
- **pandas**: Data manipulation
- **numpy**: Numerical operations
- **requests**: HTTP client

## Usage

### Streamlit App

1. **Select Benchmark**: Choose from Mini, Standard, Stratified, or Comprehensive
2. **Navigate**: Use index selector or Previous/Next buttons
3. **Adjust Intensity**: Control GenAlpha conversion strength (0.0-1.0)
4. **Compare**: Toggle GenAlpha view to see transformations
5. **Custom Convert**: Try your own text in the Custom Conversion tab

### API Usage

```python
import requests

# Get benchmarks
response = requests.get("http://localhost:8000/benchmarks")
benchmarks = response.json()

# Get a conversation
response = requests.get("http://localhost:8000/conversation/mini/0")
conversation = response.json()

# Convert text
response = requests.post(
    "http://localhost:8000/convert",
    json={"text": "I'm feeling anxious", "intensity": 0.7}
)
result = response.json()
print(result['genalpha'])  # "i'm feeling lowkey stressing"

# Convert full conversation
response = requests.post(
    "http://localhost:8000/convert_conversation?benchmark_name=mini&index=0&intensity=0.7"
)
converted = response.json()
```

## Features in Detail

### Conversation Browser
- Navigate through benchmark conversations
- View full multi-turn therapeutic dialogues
- See patient and therapist exchanges
- Track conversation metadata (ID, turns, etc.)

### GenAlpha Converter
- Real-time conversion of patient responses
- Adjustable intensity (0.0 = minimal, 1.0 = maximum)
- Side-by-side comparison view
- Preserves therapeutic meaning while adapting style

### Statistics Dashboard
- Turn distribution analysis
- Message length statistics
- Conversation complexity metrics
- Visual charts and graphs

### Custom Text Tool
- Test converter on any text
- Experiment with different intensity levels
- See what transformations occur
- Perfect for understanding the converter

## Configuration

### Streamlit Settings

Edit `streamlit_app.py` to change:

```python
USE_API = False  # Set True to use FastAPI backend
API_URL = "http://localhost:8000"  # Backend URL
```

### FastAPI Settings

Edit `backend.py` to change:

```python
# CORS settings
allow_origins=["*"]  # Restrict in production

# Port and host
uvicorn.run(app, host="0.0.0.0", port=8000)
```

## Benchmarks Available

| Benchmark | Size | Description |
|-----------|------|-------------|
| Mini | 50 | Quick testing and demos |
| Standard | 200 | Regular evaluation |
| Stratified | 300 | Balanced by complexity |
| Comprehensive | 500 | Thorough analysis |
| Evaluation Subset | 100 | Original processed subset |
| GenAlpha Subset | 100 | Pre-converted subset |

## Project Structure

```
app/
├── backend.py              # FastAPI REST API
├── streamlit_app.py        # Streamlit web UI
├── requirements.txt        # Python dependencies
├── start_backend.sh        # Launch FastAPI
├── start_streamlit.sh      # Launch Streamlit
└── README.md              # This file
```

## Development

### Running in Development Mode

**Streamlit** (auto-reloads on file changes):
```bash
streamlit run streamlit_app.py
```

**FastAPI** (auto-reloads with --reload flag):
```bash
uvicorn backend:app --reload --host 0.0.0.0 --port 8000
```

### Adding Features

**To add a new benchmark:**
1. Add file to `results/` directory
2. Update `file_mapping` in both `backend.py` and `streamlit_app.py`
3. Add to `benchmark_options` in `streamlit_app.py`

**To add new endpoints:**
1. Add route to `backend.py`
2. Update API documentation
3. Test with API docs at `/docs`

## Deployment

### Streamlit Cloud

1. Push to GitHub
2. Connect to [Streamlit Cloud](https://streamlit.io/cloud)
3. Deploy `app/streamlit_app.py`

### Docker

```dockerfile
FROM python:3.10-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

# For Streamlit
EXPOSE 8501
CMD ["streamlit", "run", "streamlit_app.py"]

# Or for FastAPI
# EXPOSE 8000
# CMD ["uvicorn", "backend:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Production Considerations

- Set `USE_API = True` in Streamlit for scalability
- Configure CORS properly in FastAPI
- Add authentication if needed
- Use environment variables for config
- Enable HTTPS
- Add rate limiting
- Cache conversation data

## Troubleshooting

**Streamlit app won't start:**
```bash
# Check if port 8501 is available
lsof -i :8501

# Try different port
streamlit run streamlit_app.py --server.port 8502
```

**FastAPI app won't start:**
```bash
# Check if port 8000 is available
lsof -i :8000

# Try different port
uvicorn backend:app --port 8001
```

**Can't load benchmarks:**
- Ensure you're running from the `app/` directory
- Check that `results/` directory exists in parent
- Verify benchmark files exist

**Conversion not working:**
- Check that `src/genalpha_converter.py` is accessible
- Verify intensity is between 0.0 and 1.0
- Try restarting the app

## Contributing

To add features:
1. Fork the repository
2. Create a feature branch
3. Test locally with both Streamlit and FastAPI
4. Submit a pull request

## License

See parent directory LICENSE file.

## Support

For issues or questions:
- Check main project README
- Review documentation in `docs/`
- Check FastAPI docs at `/docs` endpoint
