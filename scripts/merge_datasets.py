"""
merge_datasets.py

Merges chunks.jsonl (manually written Persian content) and
chunks_external.jsonl (English datasets from Hugging Face) into a single
final file: chunks_final.jsonl

Usage:
    python3 merge_datasets.py
"""

import json
from pathlib import Path


PROCESSED_DIR = Path(__file__).parent.parent / "data" / "processed"

FA_PATH = PROCESSED_DIR / "chunks.jsonl"
EXTERNAL_PATH = PROCESSED_DIR / "chunks_external.jsonl"
FINAL_PATH = PROCESSED_DIR / "chunks_final.jsonl"


def load_jsonl(path: Path):
    if not path.exists():
        print(f"Warning: File {path} not found. Skipping.")
        return []

    with path.open(encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def main():
    fa_chunks = load_jsonl(FA_PATH)
    external_chunks = load_jsonl(EXTERNAL_PATH)

    print(f"Persian chunks: {len(fa_chunks)}")
    print(f"External chunks: {len(external_chunks)}")

    all_chunks = fa_chunks + external_chunks

    # Assign unified final IDs to prevent ID conflicts between the two sources.
    for i, chunk in enumerate(all_chunks, start=1):
        chunk["id"] = f"final_{i:06d}"

    with FINAL_PATH.open("w", encoding="utf-8") as f:
        for chunk in all_chunks:
            f.write(json.dumps(chunk, ensure_ascii=False) + "\n")

    print(f"\nTotal final chunks: {len(all_chunks)}")
    print(f"Saved to: {FINAL_PATH}")


if __name__ == "__main__":
    main()