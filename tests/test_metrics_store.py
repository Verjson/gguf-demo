"""
Run identity reaching Postgres.

The pipeline has always generated a run id and passed it to the export step; it never
reached the database, so every dashboard panel averaged every run ever recorded. These
tests pin the path from RUN_ID in the environment to the INSERT statement.
"""

from __future__ import annotations

from typing import Any

import pytest

from src.metrics_store import MetricsStore, run_started_from_id


class _FakeCursor:
    def __init__(self, calls: list[tuple[str, Any]]) -> None:
        self._calls = calls

    def execute(self, sql: str, vals: Any = None) -> None:
        self._calls.append((sql, vals))

    def __enter__(self):
        return self

    def __exit__(self, *exc: object) -> None:
        return None


class _FakeConn:
    def __init__(self, calls: list[tuple[str, Any]]) -> None:
        self._calls = calls

    def cursor(self) -> _FakeCursor:
        return _FakeCursor(self._calls)

    def commit(self) -> None:
        return None

    def close(self) -> None:
        # MetricsStore._execute closes the connection explicitly. `with connect(...)`
        # in psycopg2 is a *transaction* manager and leaves the socket open for
        # refcounting to collect, which made every row's connection lifetime depend
        # on GC timing. The fake has to model the real contract.
        self.closed = True

    def __enter__(self):
        return self

    def __exit__(self, *exc: object) -> None:
        return None


@pytest.fixture
def captured_sql(monkeypatch) -> list[tuple[str, Any]]:
    calls: list[tuple[str, Any]] = []
    monkeypatch.setattr("src.metrics_store.psycopg2.connect", lambda **kw: _FakeConn(calls))
    MetricsStore._schema_ready = False
    yield calls
    MetricsStore._schema_ready = False


def _insert_call(calls: list[tuple[str, Any]]) -> tuple[str, Any]:
    inserts = [c for c in calls if c[0].startswith("INSERT INTO evaluation_metrics")]
    assert len(inserts) == 1, f"expected one INSERT, got {len(inserts)}"
    return inserts[0]


def _column_value(sql: str, vals: list[Any], column: str) -> Any:
    columns = sql[sql.index("(") + 1 : sql.index(")")].split(", ")
    return vals[columns.index(column)]


def test_run_id_from_the_environment_round_trips_into_the_insert(captured_sql, monkeypatch):
    monkeypatch.setenv("RUN_ID", "2026-08-14_181632_cpu")
    monkeypatch.delenv("RUN_STARTED_AT", raising=False)

    MetricsStore().insert(
        approach="baseline",
        question="q",
        response="a",
        metrics={"rougeL": 0.5},
        device="cpu",
        sample_id="0",
    )

    sql, vals = _insert_call(captured_sql)
    assert _column_value(sql, vals, "run_id") == "2026-08-14_181632_cpu"
    assert _column_value(sql, vals, "sample_id") == "0"
    assert _column_value(sql, vals, "run_started_at") == "2026-08-14T18:16:32+00:00"
    assert "ON CONFLICT (run_id, approach, sample_id)" in sql


def test_explicit_run_id_beats_the_environment(captured_sql, monkeypatch):
    monkeypatch.setenv("RUN_ID", "2026-08-14_181632_cpu")

    MetricsStore().insert(
        approach="rag",
        question="q",
        response="a",
        metrics={},
        device="cuda",
        run_id="2026-08-14_181632_cuda",
        run_started_at="2026-08-14T18:16:32+00:00",
        sample_id="1",
    )

    sql, vals = _insert_call(captured_sql)
    assert _column_value(sql, vals, "run_id") == "2026-08-14_181632_cuda"


def test_a_step_run_by_hand_writes_no_run_id(captured_sql, monkeypatch):
    """No RUN_ID means the row belongs to no pipeline run, and must say so with NULL."""
    monkeypatch.delenv("RUN_ID", raising=False)

    MetricsStore().insert(
        approach="baseline", question="q", response="a", metrics={}, sample_id="0"
    )

    sql, _ = _insert_call(captured_sql)
    assert "run_id" not in sql
    assert "run_started_at" not in sql


def test_run_started_at_is_omitted_when_the_id_has_no_parsable_stamp(captured_sql, monkeypatch):
    monkeypatch.setenv("RUN_ID", "adhoc-smoke-test")
    monkeypatch.delenv("RUN_STARTED_AT", raising=False)

    MetricsStore().insert(
        approach="baseline", question="q", response="a", metrics={}, sample_id="0"
    )

    sql, vals = _insert_call(captured_sql)
    assert _column_value(sql, vals, "run_id") == "adhoc-smoke-test"
    assert "run_started_at" not in sql


def test_run_lifecycle_records_expected_and_recorded_samples(captured_sql):
    store = MetricsStore()
    store.start_run(
        run_id="2026-08-14_181632_cpu",
        approach="baseline",
        expected_samples=2,
        requested_device="cpu",
        runtime="transformers",
        weight_format="safetensors",
        model_name="model",
        mlflow_run_id="mlflow-1",
    )
    store.finish_run(
        run_id="2026-08-14_181632_cpu",
        approach="baseline",
        status="completed",
        recorded_samples=2,
        actual_device="cpu",
    )

    lifecycle_sql = "\n".join(sql for sql, _ in captured_sql)
    assert "INSERT INTO evaluation_runs" in lifecycle_sql
    assert "UPDATE evaluation_runs" in lifecycle_sql


@pytest.mark.parametrize(
    "run_id,expected",
    [
        ("2026-08-14_181632_cpu", "2026-08-14T18:16:32+00:00"),
        ("2026-08-14_181632_cuda", "2026-08-14T18:16:32+00:00"),
        ("2026-08-14_181632", "2026-08-14T18:16:32+00:00"),
        ("adhoc", None),
        ("", None),
        ("2026-13-45_999999_cpu", None),
    ],
)
def test_run_started_from_id(run_id: str, expected: str | None):
    assert run_started_from_id(run_id) == expected
