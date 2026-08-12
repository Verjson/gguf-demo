"""
Rank numeric score cells as best / mid / worst for colored result tables.

Markdown cannot set cell backgrounds; we emit HTML tables with inline colors
(Cursor / VS Code preview) plus emoji markers (GitHub-safe).
"""

from __future__ import annotations

from typing import Any, Iterable, Sequence

# Metrics where smaller values win (latency / cost style).
LOWER_IS_BETTER: frozenset[str] = frozenset(
    {
        "generation_time",
        "retrieval_time",
        "time_to_response",
    }
)

# Skip ranking for constants / device flags.
SKIP_RANK: frozenset[str] = frozenset(
    {
        "cuda_used",
        "cuda_device_count",
        "cuda_available",
    }
)

_RANK_STYLE = {
    "best": ("#c6efce", "🟢"),   # green
    "mid": ("#ffeb9c", "🟡"),    # yellow
    "worst": ("#ffc7ce", "🔴"),  # red
}


def lower_is_better(metric: str) -> bool:
    return metric in LOWER_IS_BETTER


def rank_scores(
    values: Sequence[float | None],
    *,
    lower_is_better: bool = False,
) -> list[str | None]:
    """
    Return ``best`` / ``mid`` / ``worst`` / ``None`` per value.

    - Only numeric values participate; ``None`` stays unranked.
    - Single distinct numeric → no coloring.
    - Ties share the same rank (e.g. two bests).
    """
    indexed = [(i, float(v)) for i, v in enumerate(values) if v is not None]
    ranks: list[str | None] = [None] * len(values)
    if len(indexed) < 2:
        return ranks

    nums = [v for _, v in indexed]
    if max(nums) == min(nums):
        return ranks

    ordered = sorted(indexed, key=lambda iv: iv[1], reverse=not lower_is_better)
    best_val = ordered[0][1]
    worst_val = ordered[-1][1]

    for i, v in indexed:
        if v == best_val:
            ranks[i] = "best"
        elif v == worst_val:
            ranks[i] = "worst"
        else:
            ranks[i] = "mid"
    return ranks


def format_ranked_cell(
    value: Any,
    rank: str | None,
    *,
    precision: int = 4,
    html: bool = True,
) -> str:
    """Format a value with optional emoji + HTML background."""
    if value is None:
        text = "—"
    elif isinstance(value, float):
        text = f"{value:.{precision}f}"
    else:
        text = str(value)

    if not rank or rank not in _RANK_STYLE:
        return text if not html else text

    bg, emoji = _RANK_STYLE[rank]
    labeled = f"{emoji}&nbsp;{text}" if html else f"{emoji} {text}"
    if not html:
        return labeled
    return (
        f'<td style="background-color:{bg};text-align:right;white-space:nowrap">'
        f"{labeled}</td>"
    )


def html_table(
    headers: Sequence[str],
    rows: Iterable[Sequence[Any]],
    *,
    metric_col: int | None = 0,
) -> str:
    """
    Build an HTML table.

    ``rows`` cells are either plain strings or pre-built ``<td>…</td>`` snippets
    from ``format_ranked_cell(..., html=True)``.
    """
    parts = [
        '<table>',
        "<thead><tr>",
        *[f"<th>{h}</th>" for h in headers],
        "</tr></thead>",
        "<tbody>",
    ]
    for row in rows:
        parts.append("<tr>")
        for i, cell in enumerate(row):
            if isinstance(cell, str) and cell.startswith("<td"):
                parts.append(cell)
            else:
                align = "left" if metric_col is not None and i == metric_col else "right"
                parts.append(f'<td style="text-align:{align}">{cell}</td>')
        parts.append("</tr>")
    parts.extend(["</tbody>", "</table>", ""])
    return "\n".join(parts)


def ranked_metric_row(
    metric: str,
    values: Sequence[float | None],
    *,
    precision: int = 4,
) -> list[str]:
    """First cell = metric name; remaining cells are ranked HTML ``<td>``s."""
    if metric in SKIP_RANK:
        ranks = [None] * len(values)
    else:
        ranks = rank_scores(values, lower_is_better=lower_is_better(metric))
    cells = [metric]
    for val, rank in zip(values, ranks):
        cells.append(format_ranked_cell(val, rank, precision=precision, html=True))
    return cells
