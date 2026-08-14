"""
One run-id parser, agreeing with itself across every shape the pipeline generates.

There were two: one took the first two underscore-separated fields, the other tested
for a trailing `_cuda`. They agreed on `..._cpu` and `..._cuda` and disagreed on the
other half — `2026-08-14_181632_cpu_vs_cuda` matched the suffix test and a *comparison*
export was labelled a pure CUDA run, choosing the hardware its manifest was stamped
with and scoping the metrics CSV to every CUDA row ever recorded.
"""

from __future__ import annotations

from datetime import datetime, timezone

import pytest

from src.metrics_store import run_started_from_id
from src.run_id import parse_run_id
from src.run_results import _run_scope

STARTED = datetime(2026, 8, 14, 18, 16, 32, tzinfo=timezone.utc)

# Exactly what scripts/run_pipeline.sh writes: two device runs and two comparisons.
PIPELINE_RUN_IDS = [
    ("2026-08-14_181632_cpu", "cpu", STARTED),
    ("2026-08-14_181632_cuda", "cuda", STARTED),
    ("2026-08-14_181632_cpu_vs_cuda", None, STARTED),
    ("2026-08-14_181632_transformers_vs_gguf", None, STARTED),
]


@pytest.mark.parametrize("run_id,device,started", PIPELINE_RUN_IDS)
def test_parses_every_run_id_the_pipeline_generates(run_id, device, started):
    assert parse_run_id(run_id) == (device, started)


@pytest.mark.parametrize("run_id,device,started", PIPELINE_RUN_IDS)
def test_both_callers_agree_on_every_pipeline_run_id(run_id, device, started):
    """The disagreement is the defect; agreement is what the shared parser buys."""
    assert _run_scope(run_id) == (device, started)
    assert run_started_from_id(run_id) == started.isoformat()


def test_a_comparison_is_never_mistaken_for_a_device_run():
    """A suffix test read `_cpu_vs_cuda` as CUDA and stamped it with GPU hardware."""
    device, started = parse_run_id("2026-08-14_181632_cpu_vs_cuda")
    assert device is None
    assert started == STARTED


@pytest.mark.parametrize(
    "run_id,expected",
    [
        ("2026-08-14_181632", (None, STARTED)),
        ("2026-08-14_181632_fine_tuned", (None, STARTED)),
        ("adhoc", (None, None)),
        ("", (None, None)),
        (None, (None, None)),
        ("2026-13-45_999999_cpu", (None, None)),
        ("cpu", (None, None)),
        ("2026-08-14_181632_CPU", (None, STARTED)),
    ],
)
def test_shapes_that_are_not_device_runs(run_id, expected):
    assert parse_run_id(run_id) == expected
