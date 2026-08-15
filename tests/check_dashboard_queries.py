#!/usr/bin/env python3
"""
Every Grafana panel must reference something that exists.

Two failure modes this catches, both of which are invisible until someone opens
the dashboard and sees an empty panel:

  * a SQL panel naming a column that was renamed or never added — the review
    found `rougel` sitting in the schema, written by nothing, and read by
    nothing, which is the same drift in the other direction;
  * a Prometheus panel naming a metric the code does not export.

The SQL half runs each query against the real database through `docker compose
exec postgres psql`, wrapped so it plans but returns nothing. Planning is enough:
it resolves every column and function without needing rows, so this works on a
fresh volume in CI.

Run from the repo root with the stack up:

    docker compose up -d postgres
    python tests/check_dashboard_queries.py
"""

from __future__ import annotations

import json
import pathlib
import re
import subprocess
import sys

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
DASHBOARD_DIR = REPO_ROOT / "grafana" / "provisioning" / "dashboards"
METRIC_SOURCES = (
    REPO_ROOT / "src" / "mlflow_tracker.py",
    REPO_ROOT / "scripts" / "metrics_server.py",
)

# Stand-ins for what Grafana substitutes. The values only have to be
# type-correct — the point is that the query resolves, not that it matches rows.
VARIABLE_STUBS = {
    "${run:sqlstring}": "'2000-01-01_000000'",
    "${baseline_run:sqlstring}": "'2000-01-01_000000'",
    "${device:sqlstring}": "'cpu','cuda'",
    "$device": "'cpu','cuda'",
}

# Recording-rule suffixes Prometheus appends to a histogram; the base metric is
# what the code declares.
HISTOGRAM_SUFFIXES = ("_bucket", "_sum", "_count")

# PromQL identifiers that are never metric names.
PROMQL_KEYWORDS = {
    "sum", "rate", "avg", "min", "max", "count", "by", "without", "le",
    "histogram_quantile", "increase", "irate", "topk", "bottomk", "clamp_max",
    "clamp_min", "on", "ignoring", "group_left", "group_right", "offset",
    "device", "approach", "job", "instance", "and", "or", "unless",
}


def interpolate(sql: str) -> str:
    for token, value in VARIABLE_STUBS.items():
        sql = sql.replace(token, value)
    # $__timeFilter(col) -> a predicate that plans; the review noted these
    # dashboards do not actually use it, but a future panel might.
    sql = re.sub(r"\$__timeFilter\(([^)]*)\)", r"\1 > NOW() - interval '1 hour'", sql)
    sql = sql.replace("$__interval", "1m")
    return sql


def plan(sql: str) -> str | None:
    """None when the query plans cleanly, else the first line of the error."""
    wrapped = f"EXPLAIN SELECT * FROM ({sql.rstrip().rstrip(';')}) _panelcheck"
    proc = subprocess.run(
        [
            "docker", "compose", "exec", "-T", "postgres",
            "psql", "-U", "raguser", "-d", "rag_eval", "-v", "ON_ERROR_STOP=1",
            "-tAc", wrapped,
        ],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )
    if proc.returncode == 0:
        return None
    stderr = proc.stderr.strip().splitlines()
    return stderr[0] if stderr else f"psql exited {proc.returncode}"


def exported_metric_names() -> set[str]:
    """Metric names the code registers with prometheus_client."""
    names: set[str] = set()
    pattern = re.compile(
        r"(?:Counter|Gauge|Histogram|Summary)\(\s*[\"']([a-zA-Z_:][a-zA-Z0-9_:]*)[\"']"
    )
    for path in METRIC_SOURCES:
        names.update(pattern.findall(path.read_text(encoding="utf-8")))
    # prometheus_client appends _total to counters, and _bucket/_sum/_count to
    # histograms, on exposition. Built as a separate set: mutating `names` while
    # iterating it is a RuntimeError.
    derived = {f"{name}_total" for name in names}
    derived |= {f"{name}{suffix}" for name in names for suffix in HISTOGRAM_SUFFIXES}
    return names | derived


def promql_metric_names(expr: str) -> set[str]:
    """Bare identifiers in a PromQL expression that look like metric names."""
    # Drop label matchers and durations so their contents are not mistaken for
    # metric names.
    expr = re.sub(r"\{[^}]*\}", " ", expr)
    expr = re.sub(r"\[[^\]]*\]", " ", expr)
    found = set()
    for token in re.findall(r"[a-zA-Z_:][a-zA-Z0-9_:]*", expr):
        if token in PROMQL_KEYWORDS:
            continue
        found.add(token)
    return found


def walk_panels(panels: list[dict]) -> list[dict]:
    flat: list[dict] = []
    for panel in panels:
        flat.append(panel)
        flat.extend(walk_panels(panel.get("panels") or []))
    return flat


def main() -> int:
    dashboards = sorted(DASHBOARD_DIR.glob("[0-9]*.json"))
    if not dashboards:
        print(f"FAIL: no dashboards found in {DASHBOARD_DIR}", file=sys.stderr)
        return 1

    exported = exported_metric_names()
    failures: list[str] = []
    n_sql = 0
    n_prom = 0

    for path in dashboards:
        dashboard = json.loads(path.read_text(encoding="utf-8"))
        print(f"\n{path.name} — {dashboard.get('title')}")
        for panel in walk_panels(dashboard.get("panels") or []):
            title = panel.get("title") or "(untitled)"
            for target in panel.get("targets") or []:
                if target.get("rawSql"):
                    n_sql += 1
                    error = plan(interpolate(target["rawSql"]))
                    if error:
                        failures.append(f"{path.name} :: {title} :: {error}")
                        print(f"  FAIL  {title}\n        {error}")
                    else:
                        print(f"  ok    {title}")
                elif target.get("expr"):
                    n_prom += 1
                    unknown = promql_metric_names(target["expr"]) - exported
                    if unknown:
                        detail = f"metric(s) not exported by the app: {sorted(unknown)}"
                        failures.append(f"{path.name} :: {title} :: {detail}")
                        print(f"  FAIL  {title}\n        {detail}")
                    else:
                        print(f"  ok    {title}")

    print(f"\nchecked {n_sql} SQL panels and {n_prom} Prometheus panels")
    if failures:
        print(f"\n{len(failures)} panel(s) failed:", file=sys.stderr)
        for failure in failures:
            print(f"  - {failure}", file=sys.stderr)
        return 1
    print("all panels resolve")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
