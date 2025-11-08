#!/usr/bin/env python3
"""
Reassemble train chunks into original CSV file.
Generated automatically by chunk_csv.py
"""

import pandas as pd
from pathlib import Path

def reassemble():
    chunks = []
    chunk_dir = Path(__file__).parent

    # Read all chunks in order
    for i in range(10):
        chunk_file = chunk_dir / f"train_chunk_{i:03d}.csv"
        print(f"Reading {chunk_file.name}...")
        chunk_df = pd.read_csv(chunk_file)
        chunks.append(chunk_df)

    # Concatenate all chunks
    print("Concatenating chunks...")
    full_df = pd.concat(chunks, ignore_index=True)

    # Save reassembled file
    output_file = chunk_dir.parent / "train.csv"
    print(f"Saving to {output_file}...")
    full_df.to_csv(output_file, index=False)

    print(f"Done! Reassembled {len(full_df)} rows")
    print(f"Original file: 99086 rows")

    if len(full_df) == 99086:
        print("✓ Row count matches original!")
    else:
        print("✗ WARNING: Row count mismatch!")

if __name__ == "__main__":
    reassemble()
