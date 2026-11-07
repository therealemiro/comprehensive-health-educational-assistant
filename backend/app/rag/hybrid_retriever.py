"""
rag/hybrid_retriever.py

Combines semantic search results (Retriever/FAISS) with keyword-based search (BM25)
to implement Hybrid Retrieval.

Why this is useful:
Semantic search works well for general concepts, but BM25 can be more accurate
for exact terms, such as the name of a specific medication or medical test, because
it directly searches for matching words.

Combining both approaches improves retrieval recall. The Reranker then selects
the most relevant results from the combined candidate set.
"""

import pickle
import re
from pathlib import Path
from typing import List, Dict

from app.config import settings
from app.rag.retriever import Retriever

TOKEN_PATTERN = re.compile(r"[\w]+", re.UNICODE)


def _tokenize(text: str):
    return TOKEN_PATTERN.findall(text.lower())


def _normalize(scores):
    """Map scores to the [0, 1] range so they can be combined."""
    if not scores:
        return scores

    lo, hi = min(scores), max(scores)

    if hi - lo < 1e-9:
        return [1.0 for _ in scores]

    return [(s - lo) / (hi - lo) for s in scores]


class HybridRetriever:
    _instance = None

    def __init__(self):
        base_dir = Path(__file__).parent.parent.parent
        bm25_path = (base_dir / "../data/processed/bm25_index.pkl").resolve()

        if not bm25_path.exists():
            raise FileNotFoundError(
                f"BM25 index not found: {bm25_path}. "
                "Run build_bm25_index.py first."
            )

        print(f"[HybridRetriever] Loading BM25 index from: {bm25_path}")

        with bm25_path.open("rb") as f:
            self.bm25 = pickle.load(f)

        # Use the existing Retriever for embedding generation and FAISS search.
        self.dense_retriever = Retriever.get_instance()

        print("[HybridRetriever] Ready.")

    @classmethod
    def get_instance(cls) -> "HybridRetriever":
        if cls._instance is None:
            cls._instance = cls()

        return cls._instance

    def retrieve(
        self,
        query: str,
        dense_k: int = 15,
        sparse_k: int = 15,
    ) -> List[Dict]:
        # 1. Retrieve results using semantic search (dense retrieval).
        dense_results = self.dense_retriever.retrieve(
            query,
            top_k=dense_k,
        )

        dense_by_id = {r["id"]: r for r in dense_results}

        dense_scores_norm = _normalize(
            [r["similarity_score"] for r in dense_results]
        )

        for r, norm_score in zip(dense_results, dense_scores_norm):
            r["_dense_norm"] = norm_score

        # 2. Retrieve results using keyword-based search (BM25/sparse retrieval).
        tokenized_query = _tokenize(query)

        bm25_scores = self.bm25.get_scores(tokenized_query)

        top_sparse_indices = sorted(
            range(len(bm25_scores)),
            key=lambda i: bm25_scores[i],
            reverse=True,
        )[:sparse_k]

        sparse_results = []

        top_sparse_scores = [
            bm25_scores[i] for i in top_sparse_indices
        ]

        sparse_scores_norm = _normalize(top_sparse_scores)

        for idx, norm_score in zip(
            top_sparse_indices,
            sparse_scores_norm,
        ):
            meta = self.dense_retriever.metadata[idx]

            sparse_results.append(
                {
                    **meta,
                    "_sparse_norm": norm_score,
                }
            )

        # 3. Combine both result sets using a weighted sum of normalized scores (50/50).
        combined = {}

        for r in dense_results:
            combined[r["id"]] = {
                **r,
                "_dense_norm": r.get("_dense_norm", 0.0),
                "_sparse_norm": 0.0,
            }

        for r in sparse_results:
            if r["id"] in combined:
                combined[r["id"]]["_sparse_norm"] = r["_sparse_norm"]
            else:
                combined[r["id"]] = {
                    **r,
                    "_dense_norm": 0.0,
                    "_sparse_norm": r["_sparse_norm"],
                }

        for r in combined.values():
            r["hybrid_score"] = (
                0.5 * r["_dense_norm"]
                + 0.5 * r["_sparse_norm"]
            )

        merged = sorted(
            combined.values(),
            key=lambda r: r["hybrid_score"],
            reverse=True,
        )

        return merged