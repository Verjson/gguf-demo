#!/usr/bin/env python3
"""
Step 1 — Download a small corpus of domain PDFs from arXiv.

These papers become:
  - the RAG knowledge base (scripts/03_create_rag_db.py)
  - the fine-tuning corpus (scripts/05_fine_tune.py)
  - the subject matter for evaluation prompts
"""

from __future__ import annotations

import json
import logging
import os
import sys
import time
import xml.etree.ElementTree as ET
from urllib.parse import urlencode

import mlflow
import requests
import yaml
from mlflow.entities import SpanType

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.mlflow_tracker import optional_mlflow_run

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
logger = logging.getLogger(__name__)

ARXIV_API = "http://export.arxiv.org/api/query"
ATOM_NS = {"atom": "http://www.w3.org/2005/Atom"}


def load_config() -> dict:
    path = os.environ.get("CONFIG_PATH", "/app/config/config.yaml")
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


@mlflow.trace(name="search_arxiv", span_type=SpanType.TOOL)
def search_arxiv_papers(
    query: str, category: str, max_results: int, attempts: int = 4
) -> list[dict]:
    """Query arXiv Atom API and return paper metadata dicts."""
    params = {
        "search_query": f"cat:{category} AND all:{query}",
        "start": 0,
        "max_results": max_results,
        "sortBy": "relevance",
        "sortOrder": "descending",
    }
    url = f"{ARXIV_API}?{urlencode(params)}"
    for attempt in range(1, attempts + 1):
        try:
            response = requests.get(url, timeout=60)
            response.raise_for_status()
            break
        except requests.RequestException as exc:
            if attempt == attempts:
                raise
            delay = 2**attempt
            logger.warning(
                "arXiv search failed (%s); retry %d/%d in %ds", exc, attempt, attempts - 1, delay
            )
            time.sleep(delay)

    root = ET.fromstring(response.content)
    papers = []

    for entry in root.findall("atom:entry", ATOM_NS):
        paper_id = entry.find("atom:id", ATOM_NS).text.split("/")[-1]
        title = entry.find("atom:title", ATOM_NS).text.strip()
        summary = entry.find("atom:summary", ATOM_NS).text.strip()
        pdf_url = f"https://arxiv.org/pdf/{paper_id}.pdf"

        for link in entry.findall("atom:link", ATOM_NS):
            if link.get("title") == "pdf":
                pdf_url = link.get("href")
                break

        papers.append(
            {"id": paper_id, "title": title, "summary": summary, "pdf_url": pdf_url}
        )

    return papers


@mlflow.trace(name="download_pdf", span_type=SpanType.TOOL)
def download_pdf(url: str, save_path: str) -> bool:
    try:
        with requests.get(url, stream=True, timeout=120) as response:
            response.raise_for_status()
            with open(save_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
        return True
    except Exception as exc:  # noqa: BLE001
        logger.error("Failed to download %s: %s", url, exc)
        return False


def load_cached_papers(meta_path: str, data_dir: str) -> list[dict] | None:
    """Previously downloaded papers whose PDFs are still on disk, else None."""
    if not os.path.isfile(meta_path):
        return None
    try:
        with open(meta_path, encoding="utf-8") as f:
            papers = json.load(f)
    except (OSError, json.JSONDecodeError):
        return None

    present = [
        p for p in papers if os.path.isfile(os.path.join(data_dir, pdf_filename(p)))
    ]
    return present or None


def pdf_filename(paper: dict) -> str:
    return f"{paper['id'].replace('/', '_')}.pdf"


def main() -> None:
    config = load_config()
    data_dir = config.get("paths", {}).get("papers_dir", "/app/data/papers")
    os.makedirs(data_dir, exist_ok=True)

    papers_cfg = config.get("papers", {})
    meta_path = os.path.join(data_dir, "papers_metadata.json")

    logger.info("Searching arXiv (%s)...", papers_cfg.get("category", "cs.LG"))
    n_downloaded = 0
    n_cached = 0
    n_failed = 0
    used_cache = False

    with optional_mlflow_run("download_papers") as run:
        if run:
            mlflow.log_params(
                {
                    "query": papers_cfg.get("query", "machine learning"),
                    "category": papers_cfg.get("category", "cs.LG"),
                    "max_results": papers_cfg.get("max_results", 5),
                }
            )
        try:
            papers = search_arxiv_papers(
                query=papers_cfg.get("query", "machine learning"),
                category=papers_cfg.get("category", "cs.LG"),
                max_results=papers_cfg.get("max_results", 5),
            )
        except requests.RequestException as exc:
            cached = load_cached_papers(meta_path, data_dir)
            if cached is None:
                raise
            logger.warning("arXiv unreachable (%s) — reusing %d cached papers", exc, len(cached))
            papers = cached
            used_cache = True
        else:
            with open(meta_path, "w", encoding="utf-8") as f:
                json.dump(papers, f, indent=2)

        logger.info("Found %d papers. Downloading PDFs...", len(papers))
        for paper in papers:
            filename = pdf_filename(paper)
            save_path = os.path.join(data_dir, filename)
            if os.path.exists(save_path):
                logger.info("Skip existing %s", filename)
                n_cached += 1
                continue
            logger.info("Downloading: %s", paper["title"][:80])
            if download_pdf(paper["pdf_url"], save_path):
                n_downloaded += 1
            else:
                n_failed += 1
            time.sleep(1)  # arXiv fair-use guideline

        if run:
            mlflow.log_metrics(
                {
                    "n_papers": float(len(papers)),
                    "n_downloaded": float(n_downloaded),
                    "n_cached": float(n_cached),
                    "n_failed": float(n_failed),
                    "used_cache": 1.0 if used_cache else 0.0,
                }
            )
            mlflow.set_tag("stage", "download_papers")
            if os.path.isfile(meta_path):
                mlflow.log_artifact(meta_path)

    logger.info("Download complete. Metadata: %s", meta_path)


if __name__ == "__main__":
    main()
