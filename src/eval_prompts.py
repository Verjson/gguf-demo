"""
Shared evaluation prompt loading (question|ground_truth lines).
"""

from __future__ import annotations

import os


def load_evaluation_prompts(prompts_path: str | None = None) -> list[dict]:
    """Parse question|answer lines; join continuation lines into the prior answer."""
    path = prompts_path or os.environ.get(
        "PROMPTS_PATH", "/app/prompts/evaluation_prompts.txt"
    )
    prompts: list[dict] = []
    current: dict | None = None
    with open(path, encoding="utf-8") as f:
        for raw in f:
            line = raw.rstrip("\n")
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            if "|" in line:
                if current:
                    prompts.append(current)
                question, ground_truth = line.split("|", 1)
                current = {
                    "question": question.strip(),
                    "ground_truth": " ".join(ground_truth.split()),
                }
            elif current:
                current["ground_truth"] = " ".join(
                    f"{current['ground_truth']} {stripped}".split()
                )
        if current:
            prompts.append(current)
    return prompts
