"""
rag/retriever.py

Retriever class for loading the FAISS index and performing semantic search.

Important design consideration:
The embedding model and FAISS index, which take several seconds to load,
are initialized only once during the application's lifetime using the
Singleton pattern rather than once per user request. Otherwise, every chat
message would incur significant initialization overhead.
"""

import json
from pathlib import Path
from typing import List, Dict

import faiss
from sentence_transformers import SentenceTransformer

from app.config import settings


class Retriever:
    _instance = None  # Singleton instance

    def __init__(self):
        base_dir = Path(__file__).parent.parent.parent  # backend/ directory

        index_path = (base_dir / settings.vector_index_path).resolve()
        metadata_path = (base_dir / settings.vector_metadata_path).resolve()

        if not index_path.exists():
            raise FileNotFoundError(
                f"FAISS index not found: {index_path}. "
                "Run build_vector_index.py first."
            )

        if not metadata_path.exists():
            raise FileNotFoundError(
                f"Metadata file not found: {metadata_path}"
            )

        print(f"[Retriever] Loading FAISS index from: {index_path}")
        self.index = faiss.read_index(str(index_path))

        with metadata_path.open(encoding="utf-8") as f:
            self.metadata: List[Dict] = json.load(f)

        print(
            f"[Retriever] Loading embedding model: "
            f"{settings.embedding_model_name}"
        )

        self.model = SentenceTransformer(settings.embedding_model_name)

        print(
            f"[Retriever] Ready — {len(self.metadata)} chunks "
            "available in the index."
        )

    @classmethod
    def get_instance(cls) -> "Retriever":
        """
        Access the Singleton instance. The first call creates the instance,
        while subsequent calls return the same instance.
        """
        if cls._instance is None:
            cls._instance = cls()

        return cls._instance

    def retrieve(
        self,
        query: str,
        top_k: int = None,
    ) -> List[Dict]:
        """
        Return the top_k semantically similar results for a user query.

        Each result contains the chunk text, its metadata, and its similarity score.
        """
        if top_k is None:
            top_k = settings.retrieval_top_k

        query_vector = self.model.encode(
            [query],
            convert_to_numpy=True,
            normalize_embeddings=True,
        ).astype("float32")

        scores, indices = self.index.search(query_vector, top_k)

        results = []

        for score, idx in zip(scores[0], indices[0]):
            if idx == -1:  # No sufficient result was found.
                continue

            chunk_meta = self.metadata[idx]

            results.append({
                **chunk_meta,
                "similarity_score": float(score),
            })

        return results