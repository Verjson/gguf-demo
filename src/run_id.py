"""
The one parser for the run ids ``scripts/run_pipeline.sh`` generates.

A run id is a UTC stamp, optionally followed by the device that produced it::

    2026-08-14_181632_cpu               a CPU run
    2026-08-14_181632_cuda              a GPU run
    2026-08-14_181632_cpu_vs_cuda       a comparison of the two — neither device
    2026-08-14_181632_transformers_vs_gguf   a runtime comparison — neither device

There were two parsers and they disagreed on half of those shapes. One took the
first two underscore-separated fields; the other tested for a trailing ``_cuda``,
so ``..._cpu_vs_cuda`` matched and a *comparison* export was labelled a pure CUDA
run — a device that then chose the hardware its manifest was stamped with, and
scoped the metrics CSV to every CUDA row ever recorded.

Matching the whole shape rather than a suffix is what keeps the comparison ids
from being mistaken for device runs: they parse as "no device, real start time".
"""

from __future__ import annotations

import re
from datetime import datetime, timezone

RUN_ID_STAMP = "%Y-%m-%d_%H%M%S"

# The stamp, then whatever follows it. The suffix is only a device when it is
# exactly `cpu` or `cuda`; `cpu_vs_cuda` is a comparison and names no device.
_RUN_ID = re.compile(r"^(\d{4}-\d{2}-\d{2}_\d{6})(?:_(.*))?$")
_DEVICES = ("cpu", "cuda")


def parse_run_id(run_id: str | None) -> tuple[str | None, datetime | None]:
    """
    ``(device, started)`` for a run id, with ``None`` for whichever it does not name.

    Returns ``(None, None)`` for anything that is not a run id at all, which simply
    means the export is not scoped rather than that it fails.
    """
    match = _RUN_ID.match(run_id or "")
    if not match:
        return None, None
    stamp, suffix = match.group(1), match.group(2)
    try:
        started = datetime.strptime(stamp, RUN_ID_STAMP).replace(tzinfo=timezone.utc)
    except ValueError:
        return None, None
    return (suffix if suffix in _DEVICES else None), started


def run_started_at(run_id: str | None) -> str | None:
    """The ISO start time encoded in a run id, or None — for stamping database rows."""
    _, started = parse_run_id(run_id)
    return started.isoformat() if started else None


def run_group_for(run_id: str | None) -> str | None:
    """
    The stamp shared by every leg of one pipeline invocation, or None.

    ``2026-08-14_181632_cpu`` and ``2026-08-14_181632_cuda`` are two legs of the same
    run, so reporting that wants "this run" groups on ``2026-08-14_181632``. The
    dashboards compute the same value in SQL as
    ``split_part(run_id,'_',1) || '_' || split_part(run_id,'_',2)``; this is that
    expression's counterpart in Python, kept here so the two cannot drift apart the
    way the two run-id parsers this module replaced did.
    """
    match = _RUN_ID.match(run_id or "")
    return match.group(1) if match else None


def is_safe_run_id(run_id: str | None) -> bool:
    """
    Whether ``run_id`` may be used as a directory name under ``results/runs/``.

    ``export_run`` deletes ``results/runs/<run_id>`` before writing it, and the value
    arrives from ``07_export_results.py --run-id``. Without this check a value
    containing ``..`` escapes the runs directory and the recursive delete lands
    somewhere else entirely. Run ids are a known shape; anything else is refused.
    """
    if not run_id:
        return False
    return bool(_RUN_ID.match(run_id))
