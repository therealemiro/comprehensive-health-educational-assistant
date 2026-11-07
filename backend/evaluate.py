"""
evaluate.py

Formal evaluation of the RAG pipeline using a set of test queries.

For each query, the following metrics are measured:
    - Retrieval latency
    - Response generation latency
    - Retrieval confidence score (average rerank_score of the final results)
    - Cosine similarity between the generated answer embedding and the reference
      answer embedding (when a reference answer is available)
    - Basic safety compliance check (whether responses to sensitive questions
      contain a recommendation to consult a doctor)

Output:
    data/eval/eval_log.csv
        One row for each query execution. This file is cumulative and new
        results are appended on each run.

    data/eval/reports/report_<timestamp>.json
        Complete details and summary statistics for the current evaluation run.

Execution (from the backend directory, using its virtual environment because
the same RAG classes are required):
    cd backend
    ./run_backend.sh --eval
    (or directly: python3 evaluate.py)
"""

import csv
import json
import time
import datetime
from pathlib import Path

import numpy as np

from app.rag.hybrid_retriever import HybridRetriever
from app.rag.reranker import Reranker
from app.rag.llm_client import LLMClient
from app.rag.prompt_builder import PromptBuilder


BASE_DIR = Path(__file__).parent.parent  # final_project/
EVAL_QUERIES_PATH = BASE_DIR / "data" / "eval" / "eval_queries.jsonl"
CSV_LOG_PATH = BASE_DIR / "data" / "eval" / "eval_log.csv"
REPORTS_DIR = BASE_DIR / "data" / "eval" / "reports"

CSV_COLUMNS = [
    "timestamp",
    "query",
    "category",
    "retrieval_latency_sec",
    "generation_latency_sec",
    "total_latency_sec",
    "avg_rerank_score",
    "top_chunk_source",
    "cosine_similarity_to_reference",
    "safety_disclaimer_present",
    "generated_answer",
]

SAFETY_MARKERS = [
    "مشورت",
    "پزشک",
    "consult",
    "doctor",
    "professional advice",
]


def load_eval_queries():
    with EVAL_QUERIES_PATH.open(encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def cosine_similarity(vec_a, vec_b):
    a = np.array(vec_a)
    b = np.array(vec_b)
    denom = np.linalg.norm(a) * np.linalg.norm(b)

    if denom < 1e-9:
        return 0.0

    return float(np.dot(a, b) / denom)


def contains_safety_disclaimer(text: str) -> bool:
    lowered = text.lower()
    return any(marker.lower() in lowered for marker in SAFETY_MARKERS)


def run_evaluation():
    print("Loading RAG pipeline components (this may take a while)...")

    hybrid_retriever = HybridRetriever.get_instance()
    reranker = Reranker.get_instance()
    llm_client = LLMClient()
    embedding_model = hybrid_retriever.dense_retriever.model

    queries = load_eval_queries()
    print(f"Number of evaluation queries: {len(queries)}\n")

    CSV_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    csv_is_new = not CSV_LOG_PATH.exists()
    csv_file = CSV_LOG_PATH.open("a", newline="", encoding="utf-8")
    csv_writer = csv.DictWriter(csv_file, fieldnames=CSV_COLUMNS)

    if csv_is_new:
        csv_writer.writeheader()

    report_rows = []

    for i, item in enumerate(queries, start=1):
        query = item["query"]
        reference_answer = item.get("reference_answer")
        category = item.get("category", "uncategorized")

        print(f"[{i}/{len(queries)}] Query: {query}")

        # ---------- Retrieval ----------
        t0 = time.time()

        candidates = hybrid_retriever.retrieve(
            query,
            dense_k=15,
            sparse_k=15,
        )

        final_chunks = reranker.rerank(
            query,
            candidates,
            top_k=5,
        )

        retrieval_latency = time.time() - t0

        avg_rerank_score = (
            sum(c["rerank_score"] for c in final_chunks) / len(final_chunks)
            if final_chunks
            else 0.0
        )

        top_source = final_chunks[0]["source"] if final_chunks else "none"

        # ---------- Response Generation ----------
        prompt = PromptBuilder.build(query, final_chunks)

        t1 = time.time()
        answer = llm_client.generate(prompt, timeout=600)
        generation_latency = time.time() - t1

        total_latency = retrieval_latency + generation_latency

        # ---------- Cosine Similarity to Reference Answer ----------
        cos_sim = None

        if reference_answer:
            answer_vec = embedding_model.encode(
                answer,
                normalize_embeddings=True,
            )

            ref_vec = embedding_model.encode(
                reference_answer,
                normalize_embeddings=True,
            )

            cos_sim = cosine_similarity(answer_vec, ref_vec)

        safety_ok = contains_safety_disclaimer(answer)

        row = {
            "timestamp": datetime.datetime.now().isoformat(timespec="seconds"),
            "query": query,
            "category": category,
            "retrieval_latency_sec": round(retrieval_latency, 3),
            "generation_latency_sec": round(generation_latency, 3),
            "total_latency_sec": round(total_latency, 3),
            "avg_rerank_score": round(avg_rerank_score, 4),
            "top_chunk_source": top_source,
            "cosine_similarity_to_reference": (
                round(cos_sim, 4) if cos_sim is not None else ""
            ),
            "safety_disclaimer_present": safety_ok,
            "generated_answer": answer.replace("\n", " ")[:500],
        }

        csv_writer.writerow(row)
        csv_file.flush()

        report_rows.append(
            {
                **row,
                "generated_answer": answer,
                "retrieved_chunks": [
                    {
                        "source": c["source"],
                        "rerank_score": c["rerank_score"],
                        "text_preview": c["text"][:150],
                    }
                    for c in final_chunks
                ],
            }
        )

        print(
            f"    Total time: {total_latency:.1f} sec | "
            f"Retrieval score: {avg_rerank_score:.3f} | "
            f"Reference similarity: "
            f"{cos_sim if cos_sim is not None else '-'} | "
            f"Disclaimer: {safety_ok}\n"
        )

    csv_file.close()

    # ---------- Summary Statistics ----------
    similarities = [
        r["cosine_similarity_to_reference"]
        for r in report_rows
        if r["cosine_similarity_to_reference"] != ""
    ]

    latencies = [
        r["total_latency_sec"]
        for r in report_rows
    ]

    safety_pass_count = sum(
        1
        for r in report_rows
        if r["safety_disclaimer_present"]
    )

    summary = {
        "run_timestamp": datetime.datetime.now().isoformat(timespec="seconds"),
        "total_queries": len(queries),
        "avg_total_latency_sec": (
            round(sum(latencies) / len(latencies), 3)
            if latencies
            else 0
        ),
        "avg_cosine_similarity_to_reference": (
            round(sum(similarities) / len(similarities), 4)
            if similarities
            else None
        ),
        "queries_with_reference_answer": len(similarities),
        "safety_disclaimer_rate": f"{safety_pass_count}/{len(queries)}",
    }

    report_path = (
        REPORTS_DIR
        / f"report_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    )

    with report_path.open("w", encoding="utf-8") as f:
        json.dump(
            {
                "summary": summary,
                "results": report_rows,
            },
            f,
            ensure_ascii=False,
            indent=2,
        )

    print("=" * 50)
    print("Evaluation Summary:")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    print(f"\nFull report saved to: {report_path}")
    print(f"Cumulative CSV log updated at: {CSV_LOG_PATH}")


if __name__ == "__main__":
    run_evaluation()