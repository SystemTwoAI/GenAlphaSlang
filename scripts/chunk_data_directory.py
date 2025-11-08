#!/usr/bin/env python3
"""
Chunk all CSV files in the data directory for git storage.

This script finds all CSV files in the data directory that are larger than
a threshold and chunks them automatically.
"""

import argparse
from pathlib import Path
import os
import subprocess


def get_file_size_mb(filepath):
    """Get file size in megabytes."""
    return os.path.getsize(filepath) / (1024 * 1024)


def chunk_data_directory(
    data_dir: Path = Path("data"),
    output_base_dir: Path = Path("data/chunks"),
    chunk_size_mb: float = 50,
    min_size_mb: float = 10,
    dry_run: bool = False
):
    """
    Find and chunk all large CSV files in the data directory.

    Args:
        data_dir: Directory containing CSV files
        output_base_dir: Base directory for chunked outputs
        chunk_size_mb: Target size for each chunk
        min_size_mb: Minimum file size to chunk (skip smaller files)
        dry_run: If True, just show what would be done
    """
    if not data_dir.exists():
        print(f"Data directory not found: {data_dir}")
        return

    # Find all CSV files
    csv_files = list(data_dir.glob("*.csv"))

    if not csv_files:
        print(f"No CSV files found in {data_dir}")
        return

    print(f"Found {len(csv_files)} CSV file(s) in {data_dir}")
    print()

    # Process each CSV file
    files_to_chunk = []

    for csv_file in csv_files:
        size_mb = get_file_size_mb(csv_file)

        if size_mb < min_size_mb:
            print(f"✓ {csv_file.name:50s} {size_mb:8.2f} MB (too small, skipping)")
        else:
            print(f"→ {csv_file.name:50s} {size_mb:8.2f} MB (will chunk)")
            files_to_chunk.append((csv_file, size_mb))

    if not files_to_chunk:
        print("\nNo files need chunking!")
        return

    print(f"\nFiles to chunk: {len(files_to_chunk)}")

    if dry_run:
        print("\n(Dry run - no files will be created)")
        return

    # Chunk each file
    print("\nChunking files...\n")

    for csv_file, size_mb in files_to_chunk:
        print("="*70)
        print(f"Processing: {csv_file.name} ({size_mb:.2f} MB)")
        print("="*70)

        # Create output directory for this file's chunks
        output_dir = output_base_dir / csv_file.stem

        # Call chunk_csv.py script
        cmd = [
            "python", "scripts/chunk_csv.py",
            str(csv_file),
            "--output-dir", str(output_dir),
            "--chunk-size", str(chunk_size_mb)
        ]

        result = subprocess.run(cmd, capture_output=False)

        if result.returncode == 0:
            print(f"✓ Successfully chunked {csv_file.name}")
        else:
            print(f"✗ Error chunking {csv_file.name}")

        print()

    print("="*70)
    print("All files processed!")
    print("="*70)
    print(f"\nChunked files are in: {output_base_dir}/")
    print("\nTo commit to git:")
    print(f"  git add {output_base_dir}/")
    print(f"  git commit -m 'Add chunked dataset files'")


def main():
    parser = argparse.ArgumentParser(
        description="Chunk all large CSV files in data directory"
    )
    parser.add_argument("--data-dir", type=Path, default=Path("data"),
                       help="Directory containing CSV files (default: data)")
    parser.add_argument("--output-dir", type=Path, default=Path("data/chunks"),
                       help="Base directory for chunks (default: data/chunks)")
    parser.add_argument("--chunk-size", type=float, default=50,
                       help="Target chunk size in MB (default: 50)")
    parser.add_argument("--min-size", type=float, default=10,
                       help="Minimum file size to chunk in MB (default: 10)")
    parser.add_argument("--dry-run", action="store_true",
                       help="Show what would be done without doing it")

    args = parser.parse_args()

    chunk_data_directory(
        data_dir=args.data_dir,
        output_base_dir=args.output_dir,
        chunk_size_mb=args.chunk_size,
        min_size_mb=args.min_size,
        dry_run=args.dry_run
    )


if __name__ == "__main__":
    main()
