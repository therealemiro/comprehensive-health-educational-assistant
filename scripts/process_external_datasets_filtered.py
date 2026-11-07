"""
process_external_datasets_filtered.py

Revised version of process_external_datasets.py:
Instead of keeping all 182,000 MedMCQA rows (or using random sampling),
only rows whose subject_name is relevant to health education for general
users (rather than medical students) are retained.

The other datasets (MedQuAD, PubMedQA, and MedQA) are already relevant
and smaller, so they are not filtered.

Usage:
    python3 process_external_datasets_filtered.py
"""

import json
from pathlib import Path

from datasets import load_from_disk


EXTERNAL_DIR = Path(__file__).parent.parent / "data" / "external"
OUT_PATH = (
    Path(__file__).parent.parent
    / "data"
    / "processed"
    / "chunks_external.jsonl"
)

# Subjects relevant to a health education assistant for general users,
# rather than medical students.
MEDMCQA_RELEVANT_SUBJECTS = {
    "Medicine",
    "Pharmacology",
    "Pediatrics",
    "Gynaecology & Obstetrics",
    "Psychiatry",
    "Skin",
    "Ophthalmology",
    "ENT",
    "Social & Preventive Medicine",
    "Physiology",
    "Biochemistry",
    "Microbiology",
    "Dental",
}


def get_field(example: dict, candidates: list, default=""):
    for key in candidates:
        if key in example and example[key] not in (None, ""):
            return example[key]

    return default


def transform_medquad(example, idx):
    question = get_field(example, ["Question", "question", "qtext"])
    answer = get_field(example, ["Answer", "answer", "atext"])
    focus = get_field(
        example,
        ["Focus", "focus_area", "document_source"],
        default="Unknown",
    )

    if not question or not answer:
        return None

    text = f"Question: {question}\nAnswer: {answer}"

    return {
        "text": text,
        "source": "medquad_nih",
        "topic": "medical_general",
        "subtopic": str(focus).lower().replace(" ", "_"),
        "language": "en",
        "difficulty": "beginner",
        "url": "",
    }


def transform_medmcqa(example, idx):
    subject = example.get("subject_name", "")

    if subject not in MEDMCQA_RELEVANT_SUBJECTS:
        return None  # Main subject-based filter.

    question = example.get("question", "")

    options = {
        "A": example.get("opa", ""),
        "B": example.get("opb", ""),
        "C": example.get("opc", ""),
        "D": example.get("opd", ""),
    }

    correct_idx = example.get("cop", None)

    correct_letter = (
        ["A", "B", "C", "D"][correct_idx]
        if correct_idx is not None and 0 <= correct_idx <= 3
        else "?"
    )

    explanation = example.get("exp", "") or ""

    if not question:
        return None

    text = (
        f"Question: {question}\n"
        f"Options: A) {options['A']}  B) {options['B']}  "
        f"C) {options['C']}  D) {options['D']}\n"
        f"Correct answer: {correct_letter}\n"
        f"Explanation: {explanation}"
    )

    return {
        "text": text,
        "source": "medmcqa",
        "topic": "medical_exam_knowledge",
        "subtopic": str(subject)
        .lower()
        .replace(" ", "_")
        .replace("&", "and"),
        "language": "en",
        "difficulty": "advanced",
        "url": "",
    }


def transform_pubmedqa(example, idx):
    question = example.get("question", "")
    context_data = example.get("context", {}) or {}

    contexts = (
        context_data.get("contexts", [])
        if isinstance(context_data, dict)
        else []
    )

    long_answer = example.get("long_answer", "")
    final_decision = example.get("final_decision", "")

    if not question or not long_answer:
        return None

    joined_context = " ".join(contexts)

    text = (
        f"Question: {question}\n"
        f"Background: {joined_context}\n"
        f"Conclusion ({final_decision}): {long_answer}"
    )

    return {
        "text": text,
        "source": "pubmedqa",
        "topic": "medical_research",
        "subtopic": "clinical_study_findings",
        "language": "en",
        "difficulty": "advanced",
        "url": "",
    }


def transform_medqa(example, idx):
    question = get_field(example, ["question", "sent1"])
    answer = get_field(example, ["answer", "answer_idx", "label"])
    options = example.get("options", None)

    if not question:
        return None

    options_text = ""

    if isinstance(options, dict):
        options_text = "  ".join(
            f"{key}) {value}" for key, value in options.items()
        )
    elif isinstance(options, list):
        options_text = "  ".join(str(option) for option in options)

    text = f"Question: {question}\n"

    if options_text:
        text += f"Options: {options_text}\n"

    text += f"Answer: {answer}"

    return {
        "text": text,
        "source": "medqa_usmle",
        "topic": "medical_exam_knowledge",
        "subtopic": "usmle_general",
        "language": "en",
        "difficulty": "advanced",
        "url": "",
    }


DATASET_CONFIGS = [
    {
        "folder": "medquad",
        "split": "train",
        "transform": transform_medquad,
    },
    {
        "folder": "medmcqa",
        "split": "train",
        "transform": transform_medmcqa,
    },
    {
        "folder": "pubmedqa",
        "split": "train",
        "transform": transform_pubmedqa,
    },
    {
        "folder": "medqa",
        "split": "train",
        "transform": transform_medqa,
    },
]


def main():
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    total_written = 0
    total_seen = 0
    chunk_counter = 1

    with OUT_PATH.open("w", encoding="utf-8") as out_file:
        for cfg in DATASET_CONFIGS:
            folder_path = EXTERNAL_DIR / cfg["folder"]

            if not folder_path.exists():
                print(f"Skipped: Directory {folder_path} not found.")
                continue

            print(f"\nProcessing: {cfg['folder']}")

            dataset = load_from_disk(str(folder_path))
            rows = dataset[cfg["split"]]

            print(f"Total rows: {len(rows)}")

            written_this_dataset = 0

            for idx, example in enumerate(rows):
                total_seen += 1

                chunk_data = cfg["transform"](example, idx)

                if chunk_data is None:
                    continue

                chunk_data["id"] = f"ext_chunk_{chunk_counter:06d}"

                out_file.write(
                    json.dumps(chunk_data, ensure_ascii=False) + "\n"
                )

                chunk_counter += 1
                written_this_dataset += 1

            filtered_note = (
                " (after subject-based filtering)"
                if cfg["folder"] == "medmcqa"
                else ""
            )

            print(
                f"{written_this_dataset} chunks from "
                f"{cfg['folder']} written{filtered_note}."
            )

            total_written += written_this_dataset

    print(
        f"\n=== Total: {total_written} chunks saved to {OUT_PATH} "
        f"from {total_seen} processed rows ==="
    )


if __name__ == "__main__":
    main()