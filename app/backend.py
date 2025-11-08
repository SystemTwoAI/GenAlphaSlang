"""
FastAPI Backend for GenAlpha Therapy Conversation Explorer

Provides API endpoints for:
- Loading conversations from benchmarks
- Converting to GenAlpha speak
- Serving conversation data to Streamlit frontend
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional
import pandas as pd
from pathlib import Path
import sys
import re

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from genalpha_converter import GenAlphaConverter

app = FastAPI(
    title="GenAlpha Therapy API",
    description="API for exploring and converting therapy conversations to GenAlpha speak",
    version="1.0.0"
)

# CORS middleware for Streamlit
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global state
conversations_cache = {}
converter = GenAlphaConverter(intensity=0.7, use_llm=False)


class ConversationRequest(BaseModel):
    text: str
    intensity: float = 0.7


class ConversationResponse(BaseModel):
    original: str
    genalpha: str
    intensity: float


class BenchmarkInfo(BaseModel):
    name: str
    file: str
    size: int
    description: str


def parse_conversation(conversation_str):
    """Parse conversation string into structured data."""
    try:
        cleaned = conversation_str.replace("\\'", "'")
        cleaned = re.sub(r'\}\s*\n\s*\{', '},\n{', cleaned)
        conversation = eval(cleaned)
        return conversation
    except Exception as e:
        return []


@app.get("/")
async def root():
    """API root endpoint."""
    return {
        "message": "GenAlpha Therapy Conversation API",
        "version": "1.0.0",
        "endpoints": {
            "benchmarks": "/benchmarks",
            "conversations": "/conversations/{benchmark_name}",
            "conversation": "/conversation/{benchmark_name}/{index}",
            "convert": "/convert (POST)",
            "health": "/health"
        }
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}


@app.get("/benchmarks", response_model=List[BenchmarkInfo])
async def list_benchmarks():
    """List available benchmark datasets."""
    results_dir = Path(__file__).parent.parent / "results"

    benchmarks = []
    benchmark_files = {
        "mini": ("benchmark_mini_50.csv", "Mini benchmark - 50 conversations for quick testing"),
        "standard": ("benchmark_standard_200.csv", "Standard benchmark - 200 conversations for regular evaluation"),
        "stratified": ("benchmark_stratified_300.csv", "Stratified benchmark - 300 conversations balanced by complexity"),
        "comprehensive": ("benchmark_comprehensive_500.csv", "Comprehensive benchmark - 500 conversations for thorough analysis"),
        "evaluation_subset": ("evaluation_subset.csv", "Original evaluation subset - 100 conversations"),
        "evaluation_subset_genalpha": ("evaluation_subset_genalpha.csv", "GenAlpha converted subset - 100 conversations"),
    }

    for name, (file, description) in benchmark_files.items():
        file_path = results_dir / file
        if file_path.exists():
            df = pd.read_csv(file_path)
            benchmarks.append(BenchmarkInfo(
                name=name,
                file=file,
                size=len(df),
                description=description
            ))

    return benchmarks


@app.get("/conversations/{benchmark_name}")
async def get_conversations(benchmark_name: str, limit: Optional[int] = None):
    """Get all conversations from a benchmark."""
    results_dir = Path(__file__).parent.parent / "results"

    # Map benchmark name to file
    file_mapping = {
        "mini": "benchmark_mini_50.csv",
        "standard": "benchmark_standard_200.csv",
        "stratified": "benchmark_stratified_300.csv",
        "comprehensive": "benchmark_comprehensive_500.csv",
        "evaluation_subset": "evaluation_subset.csv",
        "evaluation_subset_genalpha": "evaluation_subset_genalpha.csv",
    }

    if benchmark_name not in file_mapping:
        raise HTTPException(status_code=404, detail=f"Benchmark '{benchmark_name}' not found")

    file_path = results_dir / file_mapping[benchmark_name]

    if not file_path.exists():
        raise HTTPException(status_code=404, detail=f"Benchmark file not found: {file_mapping[benchmark_name]}")

    # Load and cache
    if benchmark_name not in conversations_cache:
        df = pd.read_csv(file_path)
        conversations_cache[benchmark_name] = df
    else:
        df = conversations_cache[benchmark_name]

    if limit:
        df = df.head(limit)

    # Return summary
    return {
        "benchmark": benchmark_name,
        "total": len(df),
        "columns": df.columns.tolist(),
        "conversations": df.to_dict('records')[:limit if limit else len(df)]
    }


@app.get("/conversation/{benchmark_name}/{index}")
async def get_conversation(benchmark_name: str, index: int):
    """Get a specific conversation by index."""
    results_dir = Path(__file__).parent.parent / "results"

    file_mapping = {
        "mini": "benchmark_mini_50.csv",
        "standard": "benchmark_standard_200.csv",
        "stratified": "benchmark_stratified_300.csv",
        "comprehensive": "benchmark_comprehensive_500.csv",
        "evaluation_subset": "evaluation_subset.csv",
        "evaluation_subset_genalpha": "evaluation_subset_genalpha.csv",
    }

    if benchmark_name not in file_mapping:
        raise HTTPException(status_code=404, detail=f"Benchmark '{benchmark_name}' not found")

    file_path = results_dir / file_mapping[benchmark_name]

    if not file_path.exists():
        raise HTTPException(status_code=404, detail=f"Benchmark file not found")

    # Load data
    if benchmark_name not in conversations_cache:
        df = pd.read_csv(file_path)
        conversations_cache[benchmark_name] = df
    else:
        df = conversations_cache[benchmark_name]

    if index < 0 or index >= len(df):
        raise HTTPException(status_code=404, detail=f"Conversation index {index} out of range (0-{len(df)-1})")

    row = df.iloc[index]

    # Parse conversation if it's in the conversations column
    if 'conversations' in row:
        conv = parse_conversation(row['conversations'])

        # Extract patient and therapist turns
        patient_turns = [turn['value'] for turn in conv if turn['from'] == 'human']
        therapist_turns = [turn['value'] for turn in conv if turn['from'] == 'gpt']

        return {
            "index": index,
            "id": row.get('id', f"conv_{index}"),
            "full_conversation": conv,
            "patient_turns": patient_turns,
            "therapist_turns": therapist_turns,
            "num_turns": len(conv),
            "num_patient_turns": len(patient_turns),
            "num_therapist_turns": len(therapist_turns),
        }
    else:
        # Return raw row data
        return {
            "index": index,
            "data": row.to_dict()
        }


@app.post("/convert", response_model=ConversationResponse)
async def convert_text(request: ConversationRequest):
    """Convert text to GenAlpha speak."""
    global converter

    # Update intensity if different
    if request.intensity != converter.intensity:
        converter = GenAlphaConverter(intensity=request.intensity, use_llm=False)

    converted = converter.convert_text(request.text, context="patient")

    return ConversationResponse(
        original=request.text,
        genalpha=converted,
        intensity=request.intensity
    )


@app.post("/convert_conversation")
async def convert_conversation(benchmark_name: str, index: int, intensity: float = 0.7):
    """Convert a full conversation to GenAlpha speak."""
    # Get the conversation
    conv_data = await get_conversation(benchmark_name, index)

    if 'patient_turns' not in conv_data:
        raise HTTPException(status_code=400, detail="Cannot convert this conversation format")

    # Create converter with specified intensity
    conv = GenAlphaConverter(intensity=intensity, use_llm=False)

    # Convert patient turns
    original_patient = conv_data['patient_turns']
    genalpha_patient = [conv.convert_text(turn, context="patient") for turn in original_patient]

    # Build full conversations
    full_conv = conv_data['full_conversation']
    genalpha_conv = []

    patient_idx = 0
    for turn in full_conv:
        turn_copy = turn.copy()
        if turn['from'] == 'human':
            turn_copy['value'] = genalpha_patient[patient_idx]
            patient_idx += 1
        genalpha_conv.append(turn_copy)

    return {
        "index": index,
        "id": conv_data['id'],
        "original_conversation": full_conv,
        "genalpha_conversation": genalpha_conv,
        "patient_turns_original": original_patient,
        "patient_turns_genalpha": genalpha_patient,
        "therapist_turns": conv_data['therapist_turns'],
        "intensity": intensity
    }


@app.get("/stats/{benchmark_name}")
async def get_benchmark_stats(benchmark_name: str):
    """Get statistics for a benchmark."""
    results_dir = Path(__file__).parent.parent / "results"

    file_mapping = {
        "mini": "benchmark_mini_50.csv",
        "standard": "benchmark_standard_200.csv",
        "stratified": "benchmark_stratified_300.csv",
        "comprehensive": "benchmark_comprehensive_500.csv",
        "evaluation_subset": "evaluation_subset.csv",
    }

    if benchmark_name not in file_mapping:
        raise HTTPException(status_code=404, detail=f"Benchmark '{benchmark_name}' not found")

    file_path = results_dir / file_mapping[benchmark_name]

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Benchmark file not found")

    df = pd.read_csv(file_path)

    # Calculate statistics
    stats = {
        "total_conversations": len(df),
        "columns": df.columns.tolist(),
    }

    # If it has conversations column, analyze structure
    if 'conversations' in df.columns:
        lengths = []
        for idx, row in df.iterrows():
            conv = parse_conversation(row['conversations'])
            if conv:
                lengths.append(len(conv))

        if lengths:
            import numpy as np
            stats.update({
                "avg_turns": float(np.mean(lengths)),
                "median_turns": float(np.median(lengths)),
                "min_turns": int(np.min(lengths)),
                "max_turns": int(np.max(lengths)),
            })

    return stats


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
