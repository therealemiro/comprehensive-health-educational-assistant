"""
rag/reranker.py

Reranker class for accurately reranking initial retrieval results using a
Cross-Encoder model.

Difference from Retriever:
The Retriever is fast but approximate, as it relies on raw embedding
similarity. The Cross-Encoder is slower but more accurate because it processes
the query and each chunk together through the model instead of encoding them
separately.

For this reason, the Cross-Encoder is applied only to a small number of
initial retrieval results (for example, 20) rather than the entire collection
of approximately 210,000 chunks.

Note:
Because automatically downloading this model through the huggingface_hub
library (Xet system) was unstable on some networks, the model files were
downloaded manually using curl. The model is loaded directly from a local
directory instead of the Hugging Face Hub, eliminating runtime internet
dependency.
"""

from pathlib import Path
from typing import List, Dict

from sentence_transformers import CrossEncoder


# Local path to the manually downloaded model files (not the model name on the Hub).
LOCAL_MODEL_PATH = (
    Path(__file__).parent.parent.parent
    / "models_cache"
    / "mmarco-mMiniLMv2-L12-H384-v1"
)


class Reranker:
    _instance = None

    def __init__(self):
        if not LOCAL_MODEL_PATH.exists():
            raise FileNotFoundError(
                f"Reranker model files not found: {LOCAL_MODEL_PATH}. "
                "Download the model files manually using curl first."
            )

        print(f"[Reranker] Loading local model from: {LOCAL_MODEL_PATH}")

        self.model = CrossEncoder(
            str(LOCAL_MODEL_PATH),
            local_files_only=True,
        )

        print("[Reranker] Ready.")

    @classmethod
    def get_instance(cls) -> "Reranker":
        if cls._instance is None:
            cls._instance = cls()

        return cls._instance

    def rerank(
        self,
        query: str,
        chunks: List[Dict],
        top_k: int = 5,
    ) -> List[Dict]:
        if not chunks:
            return []

        pairs = [(query, chunk["text"]) for chunk in chunks]
        scores = self.model.predict(pairs)

        for chunk, score in zip(chunks, scores):
            chunk["rerank_score"] = float(score)

        reranked = sorted(
            chunks,
            key=lambda c: c["rerank_score"],
            reverse=True,
        )

        return reranked[:top_k]