---
date: 2026-08-14
issue:
title: Add a host-safety watchdog for long pipeline runs
---

Container limits bound the app, but nothing bounds the aggregate of the app plus Postgres, MLflow, Prometheus, Grafana and a concurrent build — and that aggregate is what drives a WSL2 VM into swap and makes the whole desktop unresponsive.

`scripts/host_guard.sh` samples `/proc/meminfo`, preferring a cgroup limit when it is itself containerized, so the same percentage thresholds hold on a laptop, a CI runner, or a slice of a shared machine. It warns as headroom shrinks, stops the app container before the kernel OOM killer picks an arbitrary victim, and reports any container that was OOM-killed so a killed eval step is not mistaken for a generic failure. Its stdout is an event stream, one line per state change plus a heartbeat.
