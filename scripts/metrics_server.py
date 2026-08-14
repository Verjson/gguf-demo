#!/usr/bin/env python3
"""
Persistent Prometheus metrics HTTP server for the app container.

Eval scripts are short-lived (`docker compose exec … python scripts/…`), so they
cannot keep :8000 open. They write into PROMETHEUS_MULTIPROC_DIR; this process
aggregates those files and serves GET /metrics for Prometheus to scrape.
"""

from __future__ import annotations

import os
import signal
import sys
import time
from pathlib import Path

# MUST set multiproc dir before importing prometheus_client metric types
MULTIPROC_DIR = Path(os.environ.get("PROMETHEUS_MULTIPROC_DIR", "/tmp/prometheus_multiproc"))
MULTIPROC_DIR.mkdir(parents=True, exist_ok=True)
os.environ["PROMETHEUS_MULTIPROC_DIR"] = str(MULTIPROC_DIR)

from wsgiref.simple_server import make_server  # noqa: E402

from prometheus_client import (  # noqa: E402
    CONTENT_TYPE_LATEST,
    CollectorRegistry,
    Gauge,
    generate_latest,
    multiprocess,
)

PORT = int(os.environ.get("METRICS_PORT", "8000"))

# Heartbeat so Prometheus stays UP even between evaluation runs
HEARTBEAT = Gauge(
    "rag_metrics_server_up",
    "1 while the persistent metrics server is running",
    multiprocess_mode="livemostrecent",
)
HEARTBEAT_TS = Gauge(
    "rag_metrics_server_heartbeat_unixtime",
    "Unix time of last metrics-server heartbeat",
    multiprocess_mode="livemostrecent",
)


def _clear_stale_multiproc_files() -> None:
    for path in MULTIPROC_DIR.glob("*.db"):
        try:
            path.unlink()
        except OSError:
            pass


def metrics_app(environ, start_response):  # noqa: ANN001
    if environ.get("PATH_INFO", "/") not in ("/", "/metrics"):
        start_response("404 Not Found", [("Content-Type", "text/plain")])
        return [b"not found\n"]

    HEARTBEAT.set(1)
    HEARTBEAT_TS.set(time.time())

    registry = CollectorRegistry()
    multiprocess.MultiProcessCollector(registry)
    payload = generate_latest(registry)
    start_response("200 OK", [("Content-Type", CONTENT_TYPE_LATEST)])
    return [payload]


def main() -> None:
    _clear_stale_multiproc_files()
    HEARTBEAT.set(1)
    HEARTBEAT_TS.set(time.time())

    httpd = make_server("0.0.0.0", PORT, metrics_app)
    print(f"metrics_server listening on 0.0.0.0:{PORT} multiproc={MULTIPROC_DIR}", flush=True)

    def _stop(*_args: object) -> None:
        print("metrics_server shutting down", flush=True)
        try:
            multiprocess.mark_process_dead(os.getpid())
        except Exception:  # noqa: BLE001
            pass
        httpd.shutdown()
        sys.exit(0)

    signal.signal(signal.SIGTERM, _stop)
    signal.signal(signal.SIGINT, _stop)
    httpd.serve_forever()


if __name__ == "__main__":
    main()
