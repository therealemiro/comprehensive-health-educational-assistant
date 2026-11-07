"""
rag/logging_utils.py

Logs real user interactions. Unlike evaluate.py, which runs only once with
predefined queries and reference answers, this module records every actual
user message processed during a chat session.

No reference answer is stored because the correct answer to a real user query
is not known in advance.

Output:
    data/eval/production_log.csv

The log is cumulative, with each processed message added as a new row.
"""

import csv
import datetime
from pathlib import Path
from typing import List, Dict

BASE_DIR = Path(__file__).parent.parent.parent.parent  # final_project/
LOG_PATH = BASE_DIR / "data" / "eval" / "production_log.csv"

CSV_COLUMNS = [
    "timestamp",
    "user_email",
    "chat_id",
    "query",
    "retrieval_latency_sec",
    "generation_latency_sec",
    "total_latency_sec",
    "avg_rerank_score",
    "top_chunk_source",
    "safety_disclaimer_present",
    "answer",
]

SAFETY_MARKERS = [
    "consult",
    "doctor",
    "professional advice",
]


def _contains_safety_disclaimer(text: str) -> bool:
    lowered = text.lower()
    return any(marker.lower() in lowered for marker in SAFETY_MARKERS)


def log_production_interaction(
    user_email: str,
    chat_id: str,
    query: str,
    answer: str,
    retrieval_latency: float,
    generation_latency: float,
    final_chunks: List[Dict],
):
    """Log each processed real user message to the cumulative CSV file."""
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)

    avg_rerank_score = (
        sum(c.get("rerank_score", 0.0) for c in final_chunks) / len(final_chunks)
        if final_chunks
        else 0.0
    )

    top_source = final_chunks[0]["source"] if final_chunks else "none"

    row = {
        "timestamp": datetime.datetime.now().isoformat(timespec="seconds"),
        "user_email": user_email,
        "chat_id": chat_id,
        "query": query,
        "retrieval_latency_sec": round(retrieval_latency, 3),
        "generation_latency_sec": round(generation_latency, 3),
        "total_latency_sec": round(
            retrieval_latency + generation_latency,
            3,
        ),
        "avg_rerank_score": round(avg_rerank_score, 4),
        "top_chunk_source": top_source,
        "safety_disclaimer_present": _contains_safety_disclaimer(answer),
        "answer": answer.replace("\n", " ")[:500],
    }

    file_is_new = not LOG_PATH.exists()

    with LOG_PATH.open("a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_COLUMNS)

        if file_is_new:
            writer.writeheader()

        writer.writerow(row)