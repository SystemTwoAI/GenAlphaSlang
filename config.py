"""
Configuration for GenAlpha Therapy Dataset

Author: Manisha Mehta (manisha.mehta@systemtwoai.com)
Date: November 2025
"""

from pathlib import Path

# ============================================================================
# PROJECT METADATA
# ============================================================================

PROJECT_NAME = "GenAlpha Therapy Conversation Evaluation"
AUTHOR = "Manisha Mehta"
AUTHOR_EMAIL = "manisha.mehta@systemtwoai.com"
VERSION = "1.0.0"

# ============================================================================
# PATHS
# ============================================================================

PROJECT_ROOT = Path(__file__).parent
DATA_DIR = PROJECT_ROOT / 'data'
RESULTS_DIR = PROJECT_ROOT / 'results'
SCRIPTS_DIR = PROJECT_ROOT / 'scripts'
SRC_DIR = PROJECT_ROOT / 'src'
DOCS_DIR = PROJECT_ROOT / 'docs'
APP_DIR = PROJECT_ROOT / 'app'

# Data subdirectories
CHUNKS_DIR = DATA_DIR / 'chunks'
EVALUATIONS_DIR = RESULTS_DIR / 'llm_evaluations'

# ============================================================================
# BENCHMARK FILES
# ============================================================================

BENCHMARKS = {
    'mini': 'benchmark_mini_50.csv',
    'standard': 'benchmark_standard_200.csv',
    'stratified': 'benchmark_stratified_300.csv',
    'comprehensive': 'benchmark_comprehensive_500.csv'
}

BENCHMARK_SIZES = {
    'mini': 50,
    'standard': 200,
    'stratified': 300,
    'comprehensive': 500
}

# ============================================================================
# LLM CONFIGURATION
# ============================================================================

# Default models for each provider
DEFAULT_MODELS = {
    'anthropic': 'claude-3-5-sonnet-20241022',
    'openai': 'gpt-4',
    'test': 'test-model'
}

# API settings
LLM_MAX_RETRIES = 3
LLM_TIMEOUT_SECONDS = 30
LLM_RATE_LIMIT_DELAY = 1.0  # seconds between requests

# Evaluation settings
DEFAULT_MAX_TURNS = 5
DEFAULT_NUM_CONVERSATIONS = 10

# ============================================================================
# ANALYSIS THRESHOLDS
# ============================================================================

# Benchmark coverage analysis
COVERAGE_SIMILARITY_THRESHOLD = 0.15  # 15% relative difference
COVERAGE_GOOD_SCORE = 80  # % of features within threshold
COVERAGE_OK_SCORE = 60

# Realism analysis
REALISM_WORD_DIVERSITY_MIN = 0.3
REALISM_WORD_DIVERSITY_TARGET = 0.5
REALISM_EMPATHY_MIN = 0.3
REALISM_QUESTION_MIN = 0.2
REALISM_COHERENCE_MIN = 0.3
REALISM_MAX_REPETITION = 10  # Maximum acceptable phrase repetition

# Therapeutic quality thresholds
THERAPEUTIC_EMPATHY_HIGH = 0.5
THERAPEUTIC_EMPATHY_MODERATE = 0.3
THERAPEUTIC_QUESTION_HIGH = 0.4
THERAPEUTIC_QUESTION_MODERATE = 0.2
THERAPEUTIC_OPEN_QUESTION_TARGET = 0.3
THERAPEUTIC_REFLECTION_TARGET = 0.2
THERAPEUTIC_VALIDATION_TARGET = 0.1

# ============================================================================
# DATASET STATISTICS (from analysis)
# ============================================================================

DATASET_TOTAL_CONVERSATIONS = 99086
DATASET_AVG_TURNS = 16.25
DATASET_AVG_PATIENT_MSG_LENGTH = 229.6  # characters
DATASET_AVG_THERAPIST_MSG_LENGTH = 271.4  # characters

# ============================================================================
# GENALPHA CONVERSION SETTINGS
# ============================================================================

GENALPHA_DEFAULT_INTENSITY = 0.7
GENALPHA_MIN_INTENSITY = 0.0
GENALPHA_MAX_INTENSITY = 1.0

# ============================================================================
# DISPLAY SETTINGS
# ============================================================================

# Conversation display
MAX_DISPLAY_TURNS = 10
MAX_MESSAGE_LENGTH = 200  # for truncation

# Analysis output
ANALYSIS_SAMPLE_SIZE = 100
ANALYSIS_RANDOM_SEED = 42

# ============================================================================
# WEB APP SETTINGS
# ============================================================================

# Streamlit
STREAMLIT_PORT = 8501
STREAMLIT_HOST = 'localhost'

# FastAPI
FASTAPI_PORT = 8000
FASTAPI_HOST = 'localhost'
FASTAPI_TITLE = "GenAlpha Therapy Conversation API"
FASTAPI_DESCRIPTION = "API for accessing therapy conversation data and GenAlpha conversions"
FASTAPI_VERSION = "1.0.0"

# ============================================================================
# LOGGING CONFIGURATION
# ============================================================================

LOG_LEVEL = 'INFO'
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
LOG_FILE = PROJECT_ROOT / 'logs' / 'genalpha.log'

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_benchmark_path(benchmark_key: str) -> Path:
    """
    Get full path to a benchmark file.

    Args:
        benchmark_key: Key from BENCHMARKS dict ('mini', 'standard', etc.)

    Returns:
        Path to benchmark file

    Raises:
        KeyError: If benchmark_key not found
    """
    if benchmark_key not in BENCHMARKS:
        raise KeyError(f"Unknown benchmark: {benchmark_key}. Choose from: {list(BENCHMARKS.keys())}")

    return RESULTS_DIR / BENCHMARKS[benchmark_key]


def ensure_directories():
    """Create necessary directories if they don't exist."""
    directories = [
        DATA_DIR,
        RESULTS_DIR,
        CHUNKS_DIR,
        EVALUATIONS_DIR,
        DOCS_DIR,
        PROJECT_ROOT / 'logs'
    ]

    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)


if __name__ == '__main__':
    # Display configuration when run directly
    print(f"{PROJECT_NAME}")
    print(f"Author: {AUTHOR} ({AUTHOR_EMAIL})")
    print(f"Version: {VERSION}")
    print(f"\nProject Root: {PROJECT_ROOT}")
    print(f"\nAvailable Benchmarks:")
    for key, filename in BENCHMARKS.items():
        size = BENCHMARK_SIZES[key]
        print(f"  {key:15} {size:4} conversations - {filename}")
