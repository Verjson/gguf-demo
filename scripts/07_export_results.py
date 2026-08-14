#!/usr/bin/env python3
"""
Step 7 — Export run results for git commit.

Snapshots processed artifacts + Postgres metrics into:
  results/runs/<YYYY-MM-DD_HHMMSS>/
  results/latest/README.md   (always the most recent export's summary)

Commit the results/ folder to track improvement over time:
  git add results/
  git commit -m "results: baseline vs RAG vs fine-tune run 2026-08-12"
"""

from __future__ import annotations

import argparse
import logging
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.run_results import export_run

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
logger = logging.getLogger(__name__)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--run-id",
        default=None,
        help="Folder name under results/runs/ (default: UTC timestamp)",
    )
    parser.add_argument(
        "--repo-root",
        default=os.environ.get("REPO_ROOT", "/app"),
        help="Repository root (default: /app in container, . on host)",
    )
    args = parser.parse_args()

    run_dir = export_run(run_id=args.run_id, repo_root=args.repo_root)

    print("\n" + "=" * 72)
    print("RUN EXPORTED")
    print("=" * 72)
    print(f"  Run folder : {run_dir}")
    print(f"  Latest copy: {args.repo_root}/results/latest/")
    print("\nCommit to git (from repo root on host):")
    print("  git add results/")
    print('  git commit -m "results: evaluation run $(basename results/runs/* | tail -1)"')
    print("=" * 72)


if __name__ == "__main__":
    main()
