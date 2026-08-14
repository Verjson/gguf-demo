---
date: 2026-08-14
issue:
title: Publish every stack port on loopback instead of all interfaces
---

Postgres, Prometheus, Grafana, MLflow and the app exporter all published to `0.0.0.0`, so
every machine on the LAN could reach them. None of them is defended: Postgres ships
`raguser`/`ragpass`, Grafana ships `admin`/`admin`, and MLflow and Prometheus have no
authentication at all — running the demo on a café or office network handed out an open
database and an open metrics store.

Measured on this WSL2 + Docker Desktop host with two throwaway containers: a `0.0.0.0` publish
accepted TCP connections on both `127.0.0.1` and the Windows LAN address `192.168.1.193`, while
a `127.0.0.1` publish accepted on loopback and was refused on the LAN address.

All five now bind `127.0.0.1`. Nothing internal changes: containers reach each other over the
compose network (`app:8000`, `postgres:5432`, `mlflow:5000`), which never used the published
ports, and `run_pipeline.sh` prints `http://localhost:<port>` URLs that resolve to the same
loopback address. Reaching the UIs from another machine is now a deliberate act — an SSH
tunnel, or an explicit override — rather than the default.
