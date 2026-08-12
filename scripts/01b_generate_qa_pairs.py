#!/usr/bin/env python3
"""
Step 1b — Generate extractive Q&A pairs from PDF chunks.

Creates data/processed/qa_pairs.jsonl with:
  {question, answer, context, paper_id, split}

These pairs drive:
  - evaluation prompts (test split)
  - LoRA instruction fine-tuning (train split)
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import random
import re
import sys

import yaml
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
logger = logging.getLogger(__name__)

CONFIG_PATH = os.environ.get("CONFIG_PATH", "/app/config/config.yaml")

# Template questions that force answers grounded in the chunk text
QUESTION_TEMPLATES = [
    "According to this passage, what is the main claim or contribution?",
    "What method or approach is described in this excerpt?",
    "What experimental result or finding is reported here?",
    "What problem does this passage say the work addresses?",
    "What limitation or future work is mentioned in this text?",
]


def load_config() -> dict:
    with open(CONFIG_PATH, encoding="utf-8") as f:
        return yaml.safe_load(f)


def first_sentences(text: str, n: int = 2) -> str:
    """Use the first 1–2 sentences as an extractive 'answer' grounded in the chunk."""
    parts = re.split(r"(?<=[.!?])\s+", text.strip())
    parts = [p.strip() for p in parts if len(p.strip()) > 40]
    if not parts:
        return text[:300].strip()
    return " ".join(parts[:n])


def chunk_to_pairs(chunk_text: str, paper_id: str, max_pairs: int = 2) -> list[dict]:
    """Build Q&A rows whose answers are extractive spans from the chunk."""
    answer = first_sentences(chunk_text, n=2)
    if len(answer) < 40:
        return []

    pairs = []
    templates = QUESTION_TEMPLATES[:]
    random.shuffle(templates)
    for template in templates[:max_pairs]:
        pairs.append(
            {
                "question": template,
                "answer": answer,
                "context": chunk_text,
                "paper_id": paper_id,
            }
        )
    return pairs


def write_prompts_file(test_pairs: list[dict], prompts_path: str) -> None:
    """Overwrite evaluation_prompts.txt with corpus-grounded question|answer lines."""
    lines = [
        "# Auto-generated from qa_pairs.jsonl test split — extractive ground truth",
        "# Format: question|ground_truth",
        "",
    ]
    for row in test_pairs:
        q = row["question"].replace("|", "/")
        a = row["answer"].replace("|", "/")
        # Keep lines readable
        if len(a) > 400:
            a = a[:400].rstrip() + "..."
        lines.append(f"{q}|{a}")

    with open(prompts_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    logger.info("Wrote %d evaluation prompts to %s", len(test_pairs), prompts_path)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", default=CONFIG_PATH)
    parser.add_argument("--max-chunks-per-pdf", type=int, default=8)
    parser.add_argument("--pairs-per-chunk", type=int, default=1)
    parser.add_argument("--test-ratio", type=float, default=0.3)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument(
        "--update-prompts",
        action="store_true",
        default=True,
        help="Rewrite prompts/evaluation_prompts.txt from the test split",
    )
    args = parser.parse_args()
    random.seed(args.seed)

    with open(args.config, encoding="utf-8") as f:
        config = yaml.safe_load(f)

    papers_dir = config.get("paths", {}).get("papers_dir", "/app/data/papers")
    processed_dir = config.get("paths", {}).get("processed_dir", "/app/data/processed")
    prompts_path = os.environ.get("PROMPTS_PATH", "/app/prompts/evaluation_prompts.txt")
    os.makedirs(processed_dir, exist_ok=True)

    pdfs = sorted(f for f in os.listdir(papers_dir) if f.endswith(".pdf"))
    if not pdfs:
        raise SystemExit(f"No PDFs in {papers_dir}. Run 01_download_papers.py first.")

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=config["chunking"]["chunk_size"],
        chunk_overlap=config["chunking"]["chunk_overlap"],
    )

    all_pairs: list[dict] = []

    # Prefer abstracts from metadata when available (cleaner answers)
    meta_path = os.path.join(papers_dir, "papers_metadata.json")
    if os.path.isfile(meta_path):
        for paper in json.loads(open(meta_path, encoding="utf-8").read()):
            summary = (paper.get("summary") or "").strip()
            title = paper.get("title") or paper.get("id")
            if len(summary) < 80:
                continue
            all_pairs.append(
                {
                    "question": f"What is the paper '{title}' about?",
                    "answer": first_sentences(summary, n=3),
                    "context": summary,
                    "paper_id": paper.get("id", title),
                }
            )
            all_pairs.append(
                {
                    "question": f"Summarize the contribution of '{title}'.",
                    "answer": first_sentences(summary, n=2),
                    "context": summary,
                    "paper_id": paper.get("id", title),
                }
            )

    for pdf_name in pdfs:
        pdf_path = os.path.join(papers_dir, pdf_name)
        paper_id = pdf_name.replace(".pdf", "")
        docs = PyPDFLoader(pdf_path).load()
        chunks = splitter.split_documents(docs)
        # Prefer middle pages (often method/results) over cover/refs
        usable = [c for c in chunks if len(c.page_content.strip()) > 200]
        usable = usable[: args.max_chunks_per_pdf]
        for chunk in usable:
            all_pairs.extend(
                chunk_to_pairs(chunk.page_content, paper_id, max_pairs=args.pairs_per_chunk)
            )

    random.shuffle(all_pairs)
    n_test = max(1, int(len(all_pairs) * args.test_ratio))
    test_pairs = all_pairs[:n_test]
    train_pairs = all_pairs[n_test:]

    for row in train_pairs:
        row["split"] = "train"
    for row in test_pairs:
        row["split"] = "test"

    out_path = os.path.join(processed_dir, "qa_pairs.jsonl")
    with open(out_path, "w", encoding="utf-8") as f:
        for row in train_pairs + test_pairs:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")

    logger.info(
        "Wrote %d train + %d test QA pairs to %s",
        len(train_pairs),
        len(test_pairs),
        out_path,
    )

    if args.update_prompts and test_pairs:
        write_prompts_file(test_pairs[:20], prompts_path)


if __name__ == "__main__":
    main()
