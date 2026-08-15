"""
The two definitions of evaluation_metrics must declare the same columns.

init-db.sql builds a fresh volume; _ENSURE_SCHEMA_STATEMENTS migrates an existing one
on every connect. They converge once a row is written, so a column added to only one
goes unnoticed until a fresh stack and an old one disagree — which is how cpu_logical,
peak_rss_mb, peak_gpu_mem_mb, runtime and weight_format came to exist in one and not
the other.
"""

from __future__ import annotations

import re
from pathlib import Path

from src.metrics_store import _ENSURE_SCHEMA_STATEMENTS

REPO_ROOT = Path(__file__).resolve().parent.parent
INIT_DB = REPO_ROOT / "init-db.sql"
# The two definitions this file exists to keep in step. Anything else that declares
# columns on evaluation_metrics is a third one, and a third one drifts unnoticed:
# scripts/migrate_metrics_table.sql sat at 22 columns while these two reached 43,
# and metrics_store still claimed to match it.
SCHEMA_AUTHORITIES = {"init-db.sql", "metrics_store.py"}

_CREATE_TABLE = re.compile(
    r"CREATE TABLE IF NOT EXISTS evaluation_metrics\s*\((.*?)\n\);", re.DOTALL | re.IGNORECASE
)
_ADD_COLUMN = re.compile(
    r"ADD COLUMN IF NOT EXISTS\s+(\"?\w+\"?)", re.IGNORECASE
)
_INDEX = re.compile(r"CREATE INDEX IF NOT EXISTS\s+(\w+)", re.IGNORECASE)


def _normalize(name: str) -> str:
    return name.strip().strip('"')


# Table-level clauses are not columns. A CHECK constraint spans several lines and its
# continuations start with things like `AND (...)`, so a naive "first word of each
# line" reading turned CONSTRAINT, CHECK and AND into column names.
_NOT_A_COLUMN = re.compile(
    r"^\s*(CONSTRAINT|CHECK|PRIMARY|FOREIGN|UNIQUE|EXCLUDE|AND|OR|\)|\()",
    re.IGNORECASE,
)


def _sql_file_columns() -> set[str]:
    body = _CREATE_TABLE.search(INIT_DB.read_text(encoding="utf-8"))
    assert body, "init-db.sql no longer contains a CREATE TABLE for evaluation_metrics"
    columns = set()
    depth = 0
    for line in body.group(1).splitlines():
        stripped = line.strip()
        # Inside a multi-line constraint body, nothing is a column declaration.
        was_nested = depth > 0
        depth += line.count("(") - line.count(")")
        if not stripped or stripped.startswith("--") or was_nested:
            continue
        if _NOT_A_COLUMN.match(stripped):
            continue
        columns.add(_normalize(stripped.split()[0]))
    return columns


def _python_columns() -> set[str]:
    columns = set()
    for stmt in _ENSURE_SCHEMA_STATEMENTS:
        if "CREATE TABLE IF NOT EXISTS EVALUATION_METRICS" in stmt.upper():
            inner = stmt[stmt.index("(") + 1 : stmt.rindex(")")]
            for line in inner.splitlines():
                line = line.strip().rstrip(",")
                if not line or line.startswith("--"):
                    continue
                columns.add(_normalize(line.split()[0]))
        match = _ADD_COLUMN.search(stmt)
        if match:
            columns.add(_normalize(match.group(1)))
    return columns


def _index_names(statements: list[str]) -> set[str]:
    return {m.group(1) for stmt in statements for m in [_INDEX.search(stmt)] if m}


def test_both_schema_definitions_declare_the_same_columns():
    sql_columns = _sql_file_columns()
    python_columns = _python_columns()

    missing_from_sql = python_columns - sql_columns
    missing_from_python = sql_columns - python_columns

    assert not missing_from_sql, (
        f"init-db.sql is missing columns that src/metrics_store.py adds: "
        f"{sorted(missing_from_sql)}"
    )
    assert not missing_from_python, (
        f"src/metrics_store.py is missing columns that init-db.sql creates: "
        f"{sorted(missing_from_python)}"
    )


def test_run_identity_columns_are_present_in_both():
    for definition, columns in (("init-db.sql", _sql_file_columns()), ("metrics_store", _python_columns())):
        assert "run_id" in columns, f"{definition} has no run_id column"
        assert "sample_id" in columns, f"{definition} has no sample_id column"
        assert "run_started_at" in columns, f"{definition} has no run_started_at column"


def test_fresh_and_existing_schema_paths_enforce_run_integrity():
    init_sql = INIT_DB.read_text(encoding="utf-8")
    migrations = "\n".join(_ENSURE_SCHEMA_STATEMENTS)
    shell_migration = (REPO_ROOT / "scripts" / "migrate_db.sh").read_text(encoding="utf-8")

    for token in (
        "evaluation_runs",
        "eval_metrics_run_identity",
        "eval_metrics_device_known",
        "eval_metrics_runtime_known",
        "eval_metrics_weight_format_known",
        "eval_metrics_quality_score_ranged",
        "eval_metrics_durations_nonnegative",
        "evaluation_runs_status_known",
        "evaluation_runs_counts_valid",
        "evaluation_runs_devices_known",
        "uq_eval_metrics_run_sample",
    ):
        assert token in init_sql
        assert token in migrations
        assert token in shell_migration


def test_both_definitions_create_the_run_id_index():
    sql_indexes = _index_names(INIT_DB.read_text(encoding="utf-8").splitlines())
    python_indexes = _index_names(list(_ENSURE_SCHEMA_STATEMENTS))

    assert "idx_eval_metrics_run_id" in sql_indexes
    assert "idx_eval_metrics_run_id" in python_indexes
    assert sql_indexes == python_indexes, (
        f"index definitions differ: only in init-db.sql {sorted(sql_indexes - python_indexes)}, "
        f"only in metrics_store {sorted(python_indexes - sql_indexes)}"
    )


def test_no_third_definition_of_the_table_exists():
    """
    Only init-db.sql and metrics_store.py may declare evaluation_metrics columns.

    ensure_schema() runs on every connect, so a standalone migration script has no job
    left to do — which is exactly why the last one drifted for so long without anyone
    noticing. A new file matching here means the parity test above no longer covers
    every definition.
    """
    this_file = Path(__file__).resolve()
    offenders = []
    for path in REPO_ROOT.rglob("*"):
        if path.name in SCHEMA_AUTHORITIES or not path.is_file():
            continue
        if path.resolve() == this_file:  # the checker names the pattern it looks for
            continue
        if path.suffix not in (".sql", ".py") or ".git" in path.parts:
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        if "evaluation_metrics" in text and (
            "ADD COLUMN" in text.upper() or "CREATE TABLE" in text.upper()
        ):
            offenders.append(str(path.relative_to(REPO_ROOT)))

    assert not offenders, (
        "a third definition of evaluation_metrics has appeared, which the parity test "
        f"above does not cover: {sorted(offenders)}"
    )
