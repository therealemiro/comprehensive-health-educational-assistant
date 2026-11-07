"""
finetune_embedding.py

Fine-tunes the paraphrase-multilingual-MiniLM-L12-v2 embedding model on
(query, relevant passage) pairs extracted from our own dataset, with the goal
of improving retrieval quality for the health domain.

Method:
    MultipleNegativesRankingLoss - a standard and proven approach for
    fine-tuning embeddings for retrieval. Each correct (query, passage) pair
    is treated as a positive pair, while the other passages in the same batch
    are used as negative examples. This eliminates the need to manually create
    negative examples.

Prerequisites:
    pip install sentence-transformers

Usage (from the scripts directory, using data_venv):
    python3 finetune_embedding.py

Output:
    models_cache/finetuned-embedding-health/
        Fine-tuned local embedding model.

    Before/after evaluation results are printed to the terminal.
"""

import json
from pathlib import Path

from sentence_transformers import SentenceTransformer, InputExample, losses
from sentence_transformers.evaluation import InformationRetrievalEvaluator
from torch.utils.data import DataLoader


PROCESSED_DIR = Path(__file__).parent.parent / "data" / "processed"
TRAIN_PATH = PROCESSED_DIR / "finetune_train_pairs.jsonl"
EVAL_PATH = PROCESSED_DIR / "finetune_eval_pairs.jsonl"

OUTPUT_MODEL_PATH = (
    Path(__file__).parent.parent
    / "backend"
    / "models_cache"
    / "finetuned-embedding-health"
)

BASE_MODEL_NAME = "paraphrase-multilingual-MiniLM-L12-v2"

BATCH_SIZE = 16
EPOCHS = 1


def load_jsonl(path: Path):
    with path.open(encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def build_ir_evaluator(
    eval_pairs,
    name: str,
) -> InformationRetrievalEvaluator:
    """
    Builds an evaluator for measuring retrieval quality rather than simple
    text similarity.

    Each evaluation question is treated as a query, and its corresponding
    passage is treated as the only relevant document. Passages associated
    with the other queries are also added to the corpus as irrelevant
    documents.

    The evaluation metrics include MRR@10 and Recall@10. Higher scores
    indicate better retrieval performance.
    """
    queries = {
        str(i): p["query"]
        for i, p in enumerate(eval_pairs)
    }

    corpus = {
        str(i): p["passage"]
        for i, p in enumerate(eval_pairs)
    }

    relevant_docs = {
        str(i): {str(i)}
        for i in range(len(eval_pairs))
    }

    return InformationRetrievalEvaluator(
        queries=queries,
        corpus=corpus,
        relevant_docs=relevant_docs,
        name=name,
        show_progress_bar=True,
    )


def main():
    train_pairs = load_jsonl(TRAIN_PATH)
    eval_pairs = load_jsonl(EVAL_PATH)

    print(
        f"Training pairs: {len(train_pairs)} | "
        f"Evaluation pairs: {len(eval_pairs)}"
    )

    print(f"\nLoading base model: {BASE_MODEL_NAME}")
    model = SentenceTransformer(BASE_MODEL_NAME)

    # ---------- Evaluation before fine-tuning ----------
    print("\n=== Evaluating retrieval quality before fine-tuning ===")

    evaluator_before = build_ir_evaluator(
        eval_pairs,
        name="before-finetune",
    )

    score_before = evaluator_before(model)

    print(f"Result before fine-tuning: {score_before}")

    # ---------- Prepare training data ----------
    train_examples = [
        InputExample(
            texts=[p["query"], p["passage"]]
        )
        for p in train_pairs
    ]

    train_dataloader = DataLoader(
        train_examples,
        shuffle=True,
        batch_size=BATCH_SIZE,
    )

    train_loss = losses.MultipleNegativesRankingLoss(model)

    # ---------- Training ----------
    print(
        f"\n=== Starting fine-tuning "
        f"({EPOCHS} epoch(s), this may take a while) ==="
    )

    model.fit(
        train_objectives=[(train_dataloader, train_loss)],
        epochs=EPOCHS,
        warmup_steps=int(0.1 * len(train_dataloader)),
        show_progress_bar=True,
    )

    # ---------- Evaluation after fine-tuning ----------
    print("\n=== Evaluating retrieval quality after fine-tuning ===")

    evaluator_after = build_ir_evaluator(
        eval_pairs,
        name="after-finetune",
    )

    score_after = evaluator_after(model)

    print(f"Result after fine-tuning: {score_after}")

    # ---------- Save the final model locally ----------
    OUTPUT_MODEL_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    model.save(str(OUTPUT_MODEL_PATH))

    print(
        f"\nFine-tuned model saved to: {OUTPUT_MODEL_PATH}"
    )

    # ---------- Comparison summary ----------
    print("\n=== Comparison Summary ===")
    print(f"Before fine-tuning: {score_before}")
    print(f"After fine-tuning : {score_after}")


if __name__ == "__main__":
    main()