---
date: 2026-08-14
issue:
title: Publish services on ports the host actually has free
---

macOS runs an AirPlay Receiver on port 5000 by default, so MLflow could not start there at all — the stack came up with a dead tracking server. Every published port is now overridable (`MLFLOW_PORT`, `GRAFANA_PORT`, `PROMETHEUS_PORT`, `POSTGRES_PORT`, `APP_PORT`), and `run_pipeline.sh` moves to the next free port when the preferred one is taken, printing where it went. Only the host side moves; services still reach each other on the container port, so nothing internal depends on the number.

A port already published by this stack's own containers does not count as a conflict. Without that check, re-running the pipeline against a live stack would see its own MLflow on 5000, move to 5001, recreate the container, and walk one port further on every subsequent run.
