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
import time
import xml.etree.ElementTree as ET
from urllib.parse import urlencode

import requests
import yaml

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
logger = logging.getLogger(__name__)

ARXIV_API = "http://export.arxiv.org/api/query"
ATOM_NS = {"atom": "http://www.w3.org/2005/Atom"}


def load_config() -> dict:
    path = os.environ.get("CONFIG_PATH", "/app/config/config.yaml")
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def search_arxiv_papers(query: str, category: str, max_results: int) -> list[dict]:
    """Query arXiv Atom API and return paper metadata dicts."""
    params = {
        "search_query": f"cat:{category} AND all:{query}",
        "start": 0,
        "max_results": max_results,
        "sortBy": "relevance",
        "sortOrder": "descending",
    }
    url = f"{ARXIV_API}?{urlencode(params)}"
    response = requests.get(url, timeout=60)
    response.raise_for_status()

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


def main() -> None:
    config = load_config()
    data_dir = config.get("paths", {}).get("papers_dir", "/app/data/papers")
    os.makedirs(data_dir, exist_ok=True)

    papers_cfg = config.get("papers", {})
    logger.info("Searching arXiv (%s)...", papers_cfg.get("category", "cs.LG"))
    papers = search_arxiv_papers(
        query=papers_cfg.get("query", "machine learning"),
        category=papers_cfg.get("category", "cs.LG"),
        max_results=papers_cfg.get("max_results", 5),
    )

    meta_path = os.path.join(data_dir, "papers_metadata.json")
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(papers, f, indent=2)

    logger.info("Found %d papers. Downloading PDFs...", len(papers))
    for paper in papers:
        filename = f"{paper['id'].replace('/', '_')}.pdf"
        save_path = os.path.join(data_dir, filename)
        if os.path.exists(save_path):
            logger.info("Skip existing %s", filename)
            continue
        logger.info("Downloading: %s", paper["title"][:80])
        download_pdf(paper["pdf_url"], save_path)
        time.sleep(1)  # arXiv fair-use guideline

    logger.info("Download complete. Metadata: %s", meta_path)


if __name__ == "__main__":
    main()
