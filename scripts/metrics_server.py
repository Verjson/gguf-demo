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
import threading
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


def _pid_is_live(pid: int) -> bool:
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True  # exists, owned by someone else
    except OSError:
        return True  # can't tell; assume live and keep the file
    return True


def _clear_stale_multiproc_files() -> None:
    """
    Drop only the files whose writing process is gone *and* whose pid has been reused.

    This used to unlink every ``*.db`` in the directory on startup. Because eval
    scripts are ephemeral and leave their files behind for this server to aggregate,
    that discarded the accumulated counters and histograms of every completed run each
    time the container was rebuilt or restarted — which happens routinely mid-session.

    Prometheus counters are supposed to survive a scraper restart; what actually has
    to be cleaned up is a file left by a dead process whose pid has since been handed
    to something else, because prometheus_client would otherwise union its values with
    the new process's. Keeping the rest preserves the history.
    """
    kept = removed = 0
    for path in MULTIPROC_DIR.glob("*.db"):
        # prometheus_client names these <type>_<pid>.db
        stem = path.stem.rsplit("_", 1)
        pid = None
        if len(stem) == 2 and stem[1].isdigit():
            pid = int(stem[1])
        if pid is not None and _pid_is_live(pid):
            kept += 1
            continue
        if pid is None:
            # Unrecognised name: leave it rather than delete data we cannot identify.
            kept += 1
            continue
        # The writer is gone. Its samples are still valid history, so keep them unless
        # RESET_METRICS asks for a clean slate.
        if os.environ.get("RESET_METRICS", "").strip().lower() in {"1", "true", "yes"}:
            try:
                path.unlink()
                removed += 1
            except OSError:
                kept += 1
        else:
            kept += 1
    print(
        f"metrics_server multiproc files: kept={kept} removed={removed} "
        f"(set RESET_METRICS=1 to discard history from exited processes)",
        flush=True,
    )


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

    # WSGIServer.shutdown() blocks until serve_forever() acknowledges it, and
    # serve_forever() runs on this thread — so calling it from a signal handler,
    # which also runs on this thread, deadlocks: the loop that has to answer is the
    # loop now sitting inside the handler. It printed "shutting down" and then hung
    # until Docker's stop timeout expired and SIGKILL arrived, every single time.
    #
    # The handler now only sets a flag; the shutdown happens from a helper thread, so
    # the serve loop is free to notice and return.
    def _stop(signum: int, _frame: object) -> None:
        print(f"metrics_server shutting down (signal {signum})", flush=True)
        threading.Thread(target=httpd.shutdown, daemon=True).start()

    signal.signal(signal.SIGTERM, _stop)
    signal.signal(signal.SIGINT, _stop)

    try:
        httpd.serve_forever()
    finally:
        # After serve_forever() has returned, so nothing is mid-scrape.
        try:
            multiprocess.mark_process_dead(os.getpid())
        except Exception:  # noqa: BLE001
            pass
        httpd.server_close()
        print("metrics_server stopped", flush=True)
        sys.stdout.flush()


if __name__ == "__main__":
    main()
