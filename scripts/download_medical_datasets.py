"""
download_medical_datasets.py

Download 4 medical datasets from Hugging Face Hub for a comprehensive health assistant.

Install prerequisites (run once on your system):
    pip install datasets huggingface_hub

Run:
    python download_medical_datasets.py

Output: Each dataset will be saved in data/external/<dataset_name>/ as parquet/json files.
"""

from datasets import load_dataset
from pathlib import Path

OUT_DIR = Path(__file__).parent.parent / "data" / "external"
OUT_DIR.mkdir(parents=True, exist_ok=True)


def download_and_save(name: str, hf_path: str, config: str = None):
    print(f"\nDownloading: {name} ({hf_path})")
    try:
        if config:
            ds = load_dataset(hf_path, config)
        else:
            ds = load_dataset(hf_path)

        save_path = OUT_DIR / name
        ds.save_to_disk(str(save_path))
        print(f"Saved to: {save_path}")

        # Display one sample for a quick format check
        first_split = list(ds.keys())[0]
        print(f"Sample from split '{first_split}':")
        print(ds[first_split][0])

    except Exception as e:
        print(f"Error downloading {name}: {e}")


if __name__ == "__main__":
    # 1. MedQuAD - Medical questions and answers from NIH sources (including medications)
    download_and_save("medquad", "lavita/MedQuAD")

    # 2. MedMCQA - Multiple-choice questions from medical entrance examinations
    download_and_save("medmcqa", "openlifescienceai/medmcqa")

    # 3. PubMedQA - Questions and answers derived from scientific article abstracts
    # Note: This dataset has multiple configs (pqa_labeled is smaller and faster for initial testing)
    download_and_save("pubmedqa", "qiaojin/PubMedQA", config="pqa_labeled")

    # 4. MedQA - Questions from the United States Medical Licensing Examination (USMLE)
    # Note: bigbio/med_qa is no longer supported (legacy script-based format)
    # Instead, we use the modern parquet version
    download_and_save("medqa", "GBaker/MedQA-USMLE-4-options")

    print("\nAll downloads are complete. You can now combine and chunk these files using build_dataset.py.")