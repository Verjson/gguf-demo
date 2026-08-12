#!/usr/bin/env python3
"""
Step 3 — Build the RAG database (PDF → chunks → pgvector).
"""

from __future__ import annotations

import json
import logging
import os
import sys
import time

import mlflow
import yaml

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.hardware import detect_hardware
from src.rag_pipeline import RAGPipeline

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
logger = logging.getLogger(__name__)

CONFIG_PATH = os.environ.get("CONFIG_PATH", "/app/config/config.yaml")


def load_config() -> dict:
    with open(CONFIG_PATH, encoding="utf-8") as f:
        return yaml.safe_load(f)


def main() -> None:
    hardware = detect_hardware()
    config = load_config()
    # Embeddings still benefit from CUDA when available; LLM load is heavy so we
    # only need embeddings here — but RAGPipeline loads the LLM too. That is OK
    # for a demo; set evaluation.skip_llm_on_index if you want to optimize later.
    pipeline = RAGPipeline(config, hardware=hardware)

    papers_dir = config.get("paths", {}).get("papers_dir", "/app/data/papers")
    processed_dir = config.get("paths", {}).get("processed_dir", "/app/data/processed")

    if not os.path.isdir(papers_dir):
        raise SystemExit(f"Papers directory not found: {papers_dir}. Run 01_download_papers.py first.")

    pdf_files = [f for f in os.listdir(papers_dir) if f.endswith(".pdf")]
    if not pdf_files:
        raise SystemExit(f"No PDFs in {papers_dir}. Run 01_download_papers.py first.")

    logger.info("Found %d PDF files | %s", len(pdf_files), hardware.summary())

    with mlflow.start_run(run_name="rag_db_creation"):
        mlflow.set_tag("device", hardware.device)
        mlflow.set_tag("cuda_available", str(hardware.cuda_available))
        mlflow.log_params(
            {
                "chunk_size": config["chunking"]["chunk_size"],
                "chunk_overlap": config["chunking"]["chunk_overlap"],
                "embedding_model": config["embeddings"]["model"],
                "num_documents": len(pdf_files),
                "collection_name": config["vector_store"]["collection_name"],
                **{k: str(v) for k, v in hardware.as_params().items()},
            }
        )

        start_time = time.time()
        pipeline.create_vector_store(papers_dir)
        creation_time = time.time() - start_time

        total_chunks = 0
        doc_stats = []
        for pdf_file in pdf_files:
            pdf_path = os.path.join(papers_dir, pdf_file)
            chunks = pipeline.process_pdf(pdf_path)
            total_chunks += len(chunks)
            doc_stats.append({"filename": pdf_file, "num_chunks": len(chunks)})

        mlflow.log_metrics(
            {
                "total_chunks": total_chunks,
                "num_documents": len(pdf_files),
                "creation_time_seconds": creation_time,
                **hardware.as_metrics(),
            }
        )

        os.makedirs(processed_dir, exist_ok=True)
        stats_path = os.path.join(processed_dir, "doc_stats.json")
        stats = {
            "total_chunks": total_chunks,
            "num_documents": len(pdf_files),
            "creation_time_seconds": creation_time,
            "hardware": hardware.as_params(),
            "document_stats": doc_stats,
        }
        with open(stats_path, "w", encoding="utf-8") as f:
            json.dump(stats, f, indent=2)
        mlflow.log_artifact(stats_path)

        with open(os.path.join(processed_dir, ".vector_store_created"), "w") as f:
            f.write("created")

        logger.info("RAG database ready (%d chunks, %.1fs)", total_chunks, creation_time)

        pipeline.load_vector_store()
        for query in ["What is the main contribution?", "Explain the methodology"]:
            context = pipeline.retrieve_context(query, k=2)
            logger.info("Test query: %s -> %d chars retrieved", query, len(context))

    pipeline.cleanup()


if __name__ == "__main__":
    main()
