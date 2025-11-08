# Dataset Chunking for Git Storage

GitHub has a 100MB file size limit. Since the therapy conversation dataset is larger than this, we need to chunk it into smaller pieces before committing to git.

## Quick Start

### Option 1: Chunk All CSV Files Automatically

```bash
# Extract your dataset CSV file(s) to the data/ directory first
# Then run:

python scripts/chunk_data_directory.py

# This will:
# - Find all CSV files in data/ larger than 10MB
# - Split them into 50MB chunks
# - Save chunks to data/chunks/
# - Create reassembly scripts
```

### Option 2: Chunk a Specific File

```bash
python scripts/chunk_csv.py data/your_file.csv --chunk-size 50
```

## Detailed Usage

### Chunking All Data Files

```bash
# Dry run - see what would be chunked without doing it
python scripts/chunk_data_directory.py --dry-run

# Chunk with default settings (50MB chunks, skip files < 10MB)
python scripts/chunk_data_directory.py

# Custom chunk size and minimum size
python scripts/chunk_data_directory.py --chunk-size 30 --min-size 5

# Custom directories
python scripts/chunk_data_directory.py \
    --data-dir path/to/csvs \
    --output-dir path/to/chunks
```

### Chunking a Single File

```bash
# Basic usage - creates chunks in <filename>_chunks/
python scripts/chunk_csv.py data/large_file.csv

# Specify output directory
python scripts/chunk_csv.py data/large_file.csv \
    --output-dir data/chunks/large_file

# Specify chunk size (in MB)
python scripts/chunk_csv.py data/large_file.csv \
    --chunk-size 30

# Custom prefix for chunk files
python scripts/chunk_csv.py data/large_file.csv \
    --prefix therapy_data
```

## What Gets Created

When you chunk a file called `SyntheticTherapyConversationsTrainCsv.csv`, the script creates:

```
data/chunks/SyntheticTherapyConversationsTrainCsv/
├── SyntheticTherapyConversationsTrainCsv_chunk_000.csv
├── SyntheticTherapyConversationsTrainCsv_chunk_001.csv
├── SyntheticTherapyConversationsTrainCsv_chunk_002.csv
├── ...
├── SyntheticTherapyConversationsTrainCsv_manifest.txt
└── reassemble_SyntheticTherapyConversationsTrainCsv.py
```

- **Chunk files**: Each chunk contains a portion of the data with the CSV header
- **Manifest file**: Lists all chunks with row ranges and sizes
- **Reassembly script**: Python script to reconstruct the original file

## Reassembling Chunks

To reconstruct the original file from chunks:

```bash
# Navigate to the chunks directory and run the reassembly script
cd data/chunks/SyntheticTherapyConversationsTrainCsv
python reassemble_SyntheticTherapyConversationsTrainCsv.py

# This creates the original file in the parent directory
```

Or manually reassemble:

```python
import pandas as pd
from pathlib import Path

chunks = []
for chunk_file in sorted(Path('data/chunks/filename').glob('*_chunk_*.csv')):
    chunks.append(pd.read_csv(chunk_file))

full_df = pd.concat(chunks, ignore_index=True)
full_df.to_csv('data/original_file.csv', index=False)
```

## Committing to Git

After chunking:

```bash
# Add the chunks directory
git add data/chunks/

# Commit
git commit -m "Add chunked dataset files

Chunked large CSV files to comply with GitHub's 100MB limit.
Use the reassembly scripts in each chunk directory to reconstruct."

# Push
git push
```

## Best Practices

1. **Chunk Size**: Default 50MB is safe (well under 100MB limit with buffer)
   - For very large files, use smaller chunks (25-30MB)
   - For moderate files, 50MB is optimal

2. **Min Size Threshold**: Files smaller than 10MB don't need chunking
   - Adjust with `--min-size` if needed

3. **Gitignore**: The original large CSV files in `data/` are gitignored
   - Only the chunks in `data/chunks/` will be committed
   - This is intentional to avoid duplication

4. **Verify Reassembly**: Always test reassembly before relying on chunks
   ```bash
   cd data/chunks/filename
   python reassemble_*.py
   # Check that row count matches manifest
   ```

## Example Workflow

```bash
# 1. Download and extract dataset to data/
unzip archive.zip -d data/

# 2. Check what needs chunking
python scripts/chunk_data_directory.py --dry-run

# 3. Chunk the files
python scripts/chunk_data_directory.py

# 4. Verify chunks were created
ls -lh data/chunks/*/

# 5. Test reassembly (optional but recommended)
cd data/chunks/SyntheticTherapyConversationsTrainCsv
python reassemble_*.py
cd ../../..

# 6. Commit chunks to git
git add data/chunks/
git commit -m "Add chunked dataset"
git push
```

## Troubleshooting

**Chunk file too large (> 100MB):**
- Reduce `--chunk-size` parameter
- Try 30MB or 25MB chunks

**Too many chunks created:**
- Increase `--chunk-size` parameter
- But stay well under 100MB

**Reassembly row count mismatch:**
- Check that all chunks are present
- Verify no chunks were corrupted
- Re-run chunking if needed

**Out of memory when chunking:**
- The script loads the entire CSV into memory
- For very large files, you may need to use a machine with more RAM
- Or use streaming chunking (modify script to use `chunksize` parameter in pandas)

## Notes

- Chunks preserve the CSV header in each file
- Chunks are numbered sequentially (000, 001, 002, ...)
- The manifest file documents the exact row ranges
- Reassembly scripts verify row counts match the original
- All chunks can be committed to git safely (< 100MB each)
