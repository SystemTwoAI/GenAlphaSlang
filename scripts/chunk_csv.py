#!/usr/bin/env python3
"""
Chunk large CSV files into smaller pieces for git storage.

This script splits large CSV files into chunks that are small enough for GitHub
(under 100MB limit). It preserves the header in each chunk.
"""

import pandas as pd
import argparse
from pathlib import Path
import os


def get_file_size_mb(filepath):
    """Get file size in megabytes."""
    return os.path.getsize(filepath) / (1024 * 1024)


def chunk_csv(
    input_file: Path,
    output_dir: Path,
    chunk_size_mb: float = 50,
    prefix: str = None
):
    """
    Split a large CSV file into smaller chunks.

    Args:
        input_file: Path to input CSV file
        output_dir: Directory to save chunks
        chunk_size_mb: Target size for each chunk in MB (default: 50MB)
        prefix: Prefix for output files (default: input filename without extension)
    """
    if not input_file.exists():
        raise FileNotFoundError(f"Input file not found: {input_file}")

    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)

    # Determine prefix
    if prefix is None:
        prefix = input_file.stem

    # Get total file size
    total_size_mb = get_file_size_mb(input_file)
    print(f"Input file: {input_file}")
    print(f"Total size: {total_size_mb:.2f} MB")

    # Estimate number of chunks needed
    estimated_chunks = int(total_size_mb / chunk_size_mb) + 1
    print(f"Target chunk size: {chunk_size_mb} MB")
    print(f"Estimated chunks: {estimated_chunks}")

    # Read the CSV to get total rows
    print("\nReading CSV file...")
    df = pd.read_csv(input_file)
    total_rows = len(df)
    print(f"Total rows: {total_rows}")

    # Calculate rows per chunk
    # Estimate based on file size and number of rows
    rows_per_chunk = int(total_rows / estimated_chunks)

    # Adjust to ensure we don't exceed chunk size
    # Add some buffer (use 90% of target size)
    target_size_bytes = chunk_size_mb * 1024 * 1024 * 0.9

    print(f"\nCalculating optimal chunk size...")

    # Create chunks
    chunk_num = 0
    chunks_created = []

    for start_idx in range(0, total_rows, rows_per_chunk):
        end_idx = min(start_idx + rows_per_chunk, total_rows)
        chunk_df = df.iloc[start_idx:end_idx]

        # Save chunk
        output_file = output_dir / f"{prefix}_chunk_{chunk_num:03d}.csv"
        chunk_df.to_csv(output_file, index=False)

        # Check size
        chunk_size = get_file_size_mb(output_file)

        print(f"Chunk {chunk_num}: rows {start_idx:6d}-{end_idx:6d} ({end_idx - start_idx:6d} rows) = {chunk_size:6.2f} MB -> {output_file.name}")

        chunks_created.append({
            'chunk_num': chunk_num,
            'filename': output_file.name,
            'start_row': start_idx,
            'end_row': end_idx,
            'num_rows': end_idx - start_idx,
            'size_mb': chunk_size
        })

        chunk_num += 1

    # Create a manifest file
    manifest_file = output_dir / f"{prefix}_manifest.txt"
    with open(manifest_file, 'w') as f:
        f.write(f"Original file: {input_file.name}\n")
        f.write(f"Total size: {total_size_mb:.2f} MB\n")
        f.write(f"Total rows: {total_rows}\n")
        f.write(f"Total chunks: {chunk_num}\n")
        f.write(f"Columns: {', '.join(df.columns.tolist())}\n")
        f.write("\n")
        f.write("Chunks:\n")
        for chunk_info in chunks_created:
            f.write(f"  {chunk_info['filename']}: rows {chunk_info['start_row']}-{chunk_info['end_row']} ({chunk_info['num_rows']} rows, {chunk_info['size_mb']:.2f} MB)\n")

    print(f"\nCreated {chunk_num} chunks")
    print(f"Manifest saved to: {manifest_file}")

    # Create reassembly script
    reassembly_script = output_dir / f"reassemble_{prefix}.py"
    with open(reassembly_script, 'w') as f:
        f.write(f"""#!/usr/bin/env python3
\"\"\"
Reassemble {prefix} chunks into original CSV file.
Generated automatically by chunk_csv.py
\"\"\"

import pandas as pd
from pathlib import Path

def reassemble():
    chunks = []
    chunk_dir = Path(__file__).parent

    # Read all chunks in order
    for i in range({chunk_num}):
        chunk_file = chunk_dir / f"{prefix}_chunk_{{i:03d}}.csv"
        print(f"Reading {{chunk_file.name}}...")
        chunk_df = pd.read_csv(chunk_file)
        chunks.append(chunk_df)

    # Concatenate all chunks
    print("Concatenating chunks...")
    full_df = pd.concat(chunks, ignore_index=True)

    # Save reassembled file
    output_file = chunk_dir.parent / "{input_file.name}"
    print(f"Saving to {{output_file}}...")
    full_df.to_csv(output_file, index=False)

    print(f"Done! Reassembled {{len(full_df)}} rows")
    print(f"Original file: {total_rows} rows")

    if len(full_df) == {total_rows}:
        print("✓ Row count matches original!")
    else:
        print("✗ WARNING: Row count mismatch!")

if __name__ == "__main__":
    reassemble()
""")

    # Make reassembly script executable
    reassembly_script.chmod(0o755)
    print(f"Reassembly script saved to: {reassembly_script}")

    return chunks_created


def main():
    parser = argparse.ArgumentParser(
        description="Chunk large CSV files for git storage"
    )
    parser.add_argument("input", type=Path,
                       help="Input CSV file to chunk")
    parser.add_argument("--output-dir", type=Path,
                       help="Output directory for chunks (default: input_filename_chunks/)")
    parser.add_argument("--chunk-size", type=float, default=50,
                       help="Target chunk size in MB (default: 50)")
    parser.add_argument("--prefix", type=str, default=None,
                       help="Prefix for output files (default: input filename)")

    args = parser.parse_args()

    # Default output directory
    if args.output_dir is None:
        args.output_dir = args.input.parent / f"{args.input.stem}_chunks"

    # Chunk the CSV
    chunk_csv(
        input_file=args.input,
        output_dir=args.output_dir,
        chunk_size_mb=args.chunk_size,
        prefix=args.prefix
    )

    print("\n" + "="*60)
    print("Chunking complete!")
    print("="*60)
    print(f"\nTo reassemble the chunks:")
    print(f"  python {args.output_dir}/reassemble_{args.prefix or args.input.stem}.py")
    print(f"\nTo commit chunks to git:")
    print(f"  git add {args.output_dir}/")
    print(f"  git commit -m 'Add chunked {args.input.name}'")


if __name__ == "__main__":
    main()
