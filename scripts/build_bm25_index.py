"""
build_bm25_index.py

Builds a BM25 index (classic keyword-based search) from the same
chunks_final.jsonl file used to build the FAISS index.

Because both indexes are built from the same file and in the same order,
the index of each chunk in BM25 exactly matches its index in
vector_metadata.json. This allows the results of both retrieval methods
to be easily combined at runtime as part of the hybrid retrieval pipeline.

Prerequisites:
    pip install rank_bm25

Usage:
    python3 build_bm25_index.py

Output:
    data/processed/bm25_index.pkl
"""

import json
import pickle
import re
from pathlib import Path

from rank_bm25 import BM25Okapi


PROCESSED_DIR = Path(__file__).parent.parent / "data" / "processed"
CHUNKS_PATH = PROCESSED_DIR / "chunks_final.jsonl"
OUT_PATH = PROCESSED_DIR / "bm25_index.pkl"

TOKEN_PATTERN = re.compile(r"[\w]+", re.UNICODE)


def tokenize(text: str):
    """Perform lightweight tokenization that works reasonably well for both Persian and English."""
    return TOKEN_PATTERN.findall(text.lower())


def main():
    if not CHUNKS_PATH.exists():
        raise FileNotFoundError(
            f"{CHUNKS_PATH} not found. Run merge_datasets.py first."
        )

    with CHUNKS_PATH.open(encoding="utf-8") as f:
        chunks = [json.loads(line) for line in f if line.strip()]

    print(f"Number of chunks for BM25 index construction: {len(chunks)}")

    print("Tokenizing documents...")
    tokenized_corpus = [tokenize(c["text"]) for c in chunks]

    print("Building BM25 index (this may take a while)...")
    bm25 = BM25Okapi(tokenized_corpus)

    with OUT_PATH.open("wb") as f:
        pickle.dump(bm25, f)

    print(f"BM25 index saved to: {OUT_PATH}")
    print(
        "Note: Because this index was built from the same chunks_final.jsonl file, "
        "each document index exactly matches its index in vector_metadata.json "
        "and can therefore be used for hybrid retrieval."
    )


if __name__ == "__main__":
    main()