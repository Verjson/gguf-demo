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
RUN_SCOPED = (
    "02-quality-latency.json",
    "03-by-question.json",
    "04-runtime.json",
    "05-run-integrity.json",
)


def test_run_integrity_dashboard_exposes_lifecycle_and_sink_evidence():
    dashboard = _load("05-run-integrity.json")
    sql = "\n".join(raw_sql for _, raw_sql in _sql_targets(dashboard))
    for field in (
        "status",
        "expected_samples",
        "recorded_samples",
        "mlflow_run_id",
        "error",
    ):
        assert field in sql


def test_by_question_device_choices_are_scoped_to_the_selected_run():
    dashboard = _load("03-by-question.json")
    device = next(variable for variable in dashboard["templating"]["list"] if variable["name"] == "device")
    assert "${run:sqlstring}" in device["query"]


def test_runtime_dashboard_reports_live_and_peak_memory_separately():
    dashboard = _load("04-runtime.json")
    summary = next(sql for panel, sql in _sql_targets(dashboard) if panel["id"] == 4)
    assert "AVG(rss_mb)" in summary
    assert "MAX(peak_rss_mb)" in summary
    assert "AVG(peak_rss_mb)" not in summary


@pytest.mark.parametrize(
    "name", ("02-quality-latency.json", "03-by-question.json", "04-runtime.json")
)
def test_aggregate_dashboards_preserve_duplicate_question_samples(name: str):
    dashboard = _load(name)
    sql = "\n".join(raw_sql for _, raw_sql in _sql_targets(dashboard))
    assert "DISTINCT ON (run_id, approach, question" not in sql
    assert "DISTINCT ON (question, approach" not in sql
    assert "sample_id" in sql


@pytest.mark.parametrize("name", ("02-quality-latency.json", "04-runtime.json"))
def test_run_headers_do_not_hide_mixed_models_or_runtimes(name: str):
    dashboard = _load(name)
    header = next(sql for panel, sql in _sql_targets(dashboard) if panel["title"].startswith("Run —"))
    assert "string_agg(DISTINCT COALESCE(runtime" in header
    assert "string_agg(DISTINCT model_name" in header


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
    unscoped = [p["title"] for p, sql in _sql_targets(dash) if "${run:sqlstring}" not in sql]
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
    # "on time range change" would never fire: the time picker is hidden.
    assert variables["run"]["refresh"] == 1, "the run list would not refresh on load"


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


@pytest.mark.parametrize("name", RUN_SCOPED)
def test_variables_are_interpolated_through_grafanas_sql_escaping(name: str):
    """
    `'$run'` pastes the value straight into a SQL string literal.

    Run ids reach the table from RUN_ID in the environment, so a crafted value would
    be interpolated into every panel's query with the datasource's own privileges.
    `${run:sqlstring}` makes Grafana quote and escape it instead.
    """
    dash = _load(name)
    for panel, sql in _sql_targets(dash):
        assert "'$" not in sql, (
            f"{name} :: {panel['title']} quotes a variable by hand instead of :sqlstring"
        )


@pytest.mark.parametrize("name", RUN_SCOPED)
def test_the_run_picker_only_offers_well_formed_run_stamps(name: str):
    dash = _load(name)
    for variable in dash["templating"]["list"]:
        if variable["name"] in ("run", "baseline_run"):
            assert variable["regex"], f"{name} :: {variable['name']} accepts any value"
