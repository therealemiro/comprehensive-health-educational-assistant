"""
prepare_finetune_pairs.py

Extracts (query, relevant passage) pairs from chunks_final.jsonl for
fine-tuning the embedding model.

A large portion of our chunks (MedQuAD, PubMedQA, MedQA, and MedMCQA)
follow a consistent format:

    "Question: ...\n..."

This format was created by the process_external_datasets_*.py scripts,
so the question can be directly extracted from each chunk and used as
a (query, passage) pair for training.

Usage:
    python3 prepare_finetune_pairs.py

Output:
    data/processed/finetune_train_pairs.jsonl
    data/processed/finetune_eval_pairs.jsonl
        Used for evaluating retrieval quality before and after fine-tuning.
"""

import json
import random
import re
from pathlib import Path


PROCESSED_DIR = Path(__file__).parent.parent / "data" / "processed"

CHUNKS_PATH = PROCESSED_DIR / "chunks_final.jsonl"

TRAIN_OUT = PROCESSED_DIR / "finetune_train_pairs.jsonl"
EVAL_OUT = PROCESSED_DIR / "finetune_eval_pairs.jsonl"

# Maximum number of training pairs because training is slower than
# inference when running on a CPU.
MAX_TRAIN_PAIRS = 20000

EVAL_HOLD_OUT = 300
RANDOM_SEED = 42

QUESTION_PATTERN = re.compile(
    r"^Question:\s*(.+?)\n(.+)$",
    re.DOTALL,
)


def extract_pair(text: str):
    """
    If the text starts with the 'Question: ...' pattern, return
    (question, remaining passage); otherwise, return None.
    """
    match = QUESTION_PATTERN.match(text)

    if not match:
        return None

    question = match.group(1).strip()
    passage = match.group(2).strip()

    if len(question) < 10 or len(passage) < 20:
        return None

    return question, passage


def main():
    if not CHUNKS_PATH.exists():
        raise FileNotFoundError(
            f"{CHUNKS_PATH} not found."
        )

    pairs = []

    with CHUNKS_PATH.open(encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue

            chunk = json.loads(line)
            pair = extract_pair(chunk["text"])

            if pair:
                pairs.append(
                    {
                        "query": pair[0],
                        "passage": pair[1],
                        "source": chunk.get("source", ""),
                    }
                )

    print(f"Total extractable pairs: {len(pairs)}")

    random.seed(RANDOM_SEED)
    random.shuffle(pairs)

    eval_pairs = pairs[:EVAL_HOLD_OUT]
    remaining = pairs[EVAL_HOLD_OUT:]

    train_pairs = remaining[:MAX_TRAIN_PAIRS]

    with TRAIN_OUT.open("w", encoding="utf-8") as f:
        for p in train_pairs:
            f.write(json.dumps(p, ensure_ascii=False) + "\n")

    with EVAL_OUT.open("w", encoding="utf-8") as f:
        for p in eval_pairs:
            f.write(json.dumps(p, ensure_ascii=False) + "\n")

    print(
        f"Training pairs ({len(train_pairs)}) saved to: {TRAIN_OUT}"
    )

    print(
        f"Evaluation pairs ({len(eval_pairs)}) saved to: {EVAL_OUT}"
    )


if __name__ == "__main__":
    main()