"""
Dashboard invariants that keep a panel from answering a question nobody asked.

Every Postgres panel used to aggregate the whole evaluation_metrics table for all
time, while a time picker sat on top filtering nothing — so with a persistent volume
the "results" were the average of every run ever recorded. These tests pin the run
scoping that replaced it.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

DASHBOARDS = Path(__file__).resolve().parent.parent / "grafana" / "provisioning" / "dashboards"
# 01 is Prometheus-backed: a live scrape is a genuine time series and stays time-scoped.
RUN_SCOPED = ("02-quality-latency.json", "03-by-question.json", "04-runtime.json")


def _load(name: str) -> dict:
    return json.loads((DASHBOARDS / name).read_text(encoding="utf-8"))


def _sql_targets(dash: dict):
    for panel in dash["panels"]:
        for target in panel.get("targets") or []:
            if "rawSql" in target:
                yield panel, target["rawSql"]


@pytest.mark.parametrize("name", RUN_SCOPED)
def test_every_sql_panel_is_scoped_to_the_selected_run(name: str):
    dash = _load(name)
    unscoped = [p["title"] for p, sql in _sql_targets(dash) if "$run" not in sql]
    assert not unscoped, f"{name} has panels that aggregate across runs: {unscoped}"


@pytest.mark.parametrize("name", RUN_SCOPED)
def test_run_scoped_dashboards_exclude_rows_with_no_run(name: str):
    """Rows written before run_id existed belong to no run and must not be averaged in."""
    dash = _load(name)
    for panel, sql in _sql_targets(dash):
        assert "run_id IS NOT NULL" in sql, f"{name} :: {panel['title']} can match NULL run_id"


@pytest.mark.parametrize("name", RUN_SCOPED)
def test_run_picker_exists_and_lists_newest_first(name: str):
    dash = _load(name)
    variables = {v["name"]: v for v in dash["templating"]["list"]}
    assert "run" in variables, f"{name} has no run picker"
    query = variables["run"]["query"]
    assert "ORDER BY 1 DESC" in query
    assert "run_id IS NOT NULL" in query


@pytest.mark.parametrize("name", RUN_SCOPED)
def test_the_time_picker_is_hidden_where_it_filters_nothing(name: str):
    """A visible control that changes no query is worse than no control."""
    dash = _load(name)
    assert dash.get("timepicker", {}).get("hidden") is True, f"{name} still shows a time picker"
    for panel, sql in _sql_targets(dash):
        assert "$__timeFilter" not in sql, (
            f"{name} :: {panel['title']} filters on time, so the picker must not be hidden"
        )


def test_live_ops_stays_time_scoped_and_has_no_sql():
    """The Prometheus dashboard is a real time series; run scoping does not apply."""
    dash = _load("01-live-ops.json")
    assert list(_sql_targets(dash)) == []
    assert dash.get("timepicker", {}).get("hidden") is not True


def test_cross_device_panels_join_within_one_run():
    """
    The speedup panels divide a CPU latency by a GPU latency. Joining on approach alone
    let those legs come from different runs — different model, prompts and thread
    budget — and printed the quotient as a headline number.
    """
    speedup = next(
        sql
        for panel, sql in _sql_targets(_load("02-quality-latency.json"))
        if "gpu_speedup_x" in sql
    )
    assert "c.run_group = g.run_group" in speedup
    assert "c.approach = g.approach" in speedup


@pytest.mark.parametrize("name", RUN_SCOPED)
def test_aggregate_panels_report_how_many_answers_they_averaged(name: str):
    """A 3-question smoke run and a 50-question run must not render identically."""
    dash = _load(name)
    for panel, sql in _sql_targets(dash):
        if "AVG(" not in sql:
            continue
        assert "COUNT(*)" in sql or "n=" in sql, (
            f"{name} :: {panel['title']} shows an average with no n"
        )


@pytest.mark.parametrize("name", RUN_SCOPED)
def test_every_dashboard_leads_with_the_run_header(name: str):
    dash = _load(name)
    header = min(dash["panels"], key=lambda p: (p["gridPos"]["y"], p["gridPos"]["x"]))
    top_sql = [p for p in dash["panels"] if p["gridPos"]["y"] <= header["gridPos"]["y"] + 3]
    titles = [p.get("title", "") for p in top_sql]
    assert any("Run —" in t for t in titles), f"{name} has no run header near the top: {titles}"
