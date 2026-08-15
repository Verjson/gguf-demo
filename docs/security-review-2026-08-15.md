# Adversarial engineering and security review — 2026-08-15

## Review baseline and scope

The review started from `main` at
`d85504d54ec3694bfbd030949d0250a3d55e840c`. It covered application code,
dependency resolution, model downloads, both Python images, the Compose stack,
fresh and existing database schemas, MLflow/Prometheus run logging, and all
provisioned Grafana dashboards.

This is a local evaluation environment, not an internet-facing production service.
All published ports are loopback-only. MLflow and Prometheus do not provide end-user
authentication, and the demo database credentials are not production secrets; do not
expose these services through a public listener or reverse proxy without adding an
authentication boundary and real secret management.

## Outcomes

| Area | Finding | Resolution |
|---|---|---|
| Model loading | Transformers 4.57.6 was affected by model-loading code-execution advisories. | Upgraded to 5.15.0 and pinned reviewed model revisions. |
| Evaluation integrity | Duplicate question text collapsed independent samples, and missing answers or sink failures could still leave a green run. | Added stable `sample_id`, fail-closed pipeline semantics, and expected/recorded sample checks. |
| LLM judge | The cache lookup used the same value for a miss and a cached failure, preventing the intended uncached path from behaving correctly. | Added an explicit sentinel and behavioral coverage. |
| Database lifecycle | Completed, failed, and zero-row stages had no durable parent record. Fresh and migrated schemas could diverge. | Added `evaluation_runs`, additive constraints/indexes, migration drift checks, and parity tests. |
| MLflow | Pipeline runs tolerated unavailable tracking, lacked source/run correlation, and wildcard host/CORS settings disabled security middleware. | Pipeline tracking is required, runs carry run/group/source tags, and MLflow uses an explicit Compose/loopback host allowlist. |
| Prometheus | Metrics lacked run identity and dead multiprocess shards accumulated across stack starts. | Added controlled run/device/approach labels, lifecycle/sample gauges, and startup shard cleanup. |
| Grafana | Panels could mix runs, collapse duplicate prompts, hide mixed runtimes/models, and average a cumulative RSS peak as if it were live memory. | Added run-scoped queries, a Run Integrity dashboard, sample-based identity, explicit mixed values, and separate average-live/maximum-peak RSS. |
| File/network boundaries | Comparison output could escape `results/runs`; arXiv redirects could bypass the first host check; model preload arguments entered Python source. | Added resolved-path containment, redirect/final-host validation, streamed size/type checks, and environment-based preload arguments. |
| Containers | Large ignored assets entered build context, source edits invalidated the dependency layer, mutable code mounts and broad process privileges increased blast radius, and Grafana used a default admin password. | Added `.dockerignore`, dependency-first layers, non-root users, read-only roots/code mounts, dropped capabilities, `no-new-privileges`, loopback ports, and a required Grafana secret. |
| Dependencies | Direct dependency declarations were duplicated and transitive versions drifted. `langchain-community` is sunset. | `pyproject.toml` is the direct authority, `requirements.lock` constrains both images, and a small `pypdf` adapter replaces the sunset loader. |
| Images | `ankane/pgvector:latest` was an old PostgreSQL 15.4/pgvector 0.5.1 image and infrastructure tags floated. | Pinned reviewed digests for Python 3.14.7, pgvector 0.8.6/PostgreSQL 15, Prometheus 3.13.2, and Grafana 13.1.3. |

No direct SQL injection, unsafe YAML loading, or unsafe project-owned pickle
deserialization was found. SQL writes use parameters; Grafana connects through a
role whose write attempts are denied.

## Compatibility decisions

PostgreSQL remains on major 15. Moving an existing named volume directly to
PostgreSQL 18 is not an ordinary image update: it requires a tested dump/restore or
`pg_upgrade` procedure. The extension and operating-system image are current within
the retained major. [ADR 0001](decisions/0001-required-run-observability/README.md)
records this and the fail-closed observability decision.

The CPU app image is approximately 650 MB after the changes, down from the reviewed
3.65 GB baseline. CUDA 13 remains the preferred Torch path. The available prebuilt
llama-cpp-python CUDA wheel targets CUDA 12.4, so CUDA 13 builds intentionally use its
CPU GGUF wheel rather than downloading an incompatible 1.9 GB wheel that cannot load.

## Residual dependency risk

- [#27](https://github.com/Verjson/gguf-demo/issues/27): MLflow 3.15.1 requires
  `cryptography<50`, while `PYSEC-2026-3552` is fixed in 50.0.0. The project does not
  call the affected PKCS#7 decrypt APIs, but the vulnerable package remains present.
- [#28](https://github.com/Verjson/gguf-demo/issues/28): llama-cpp-python requires
  diskcache 5.6.3. `PYSEC-2026-2447` has no fixed release; exploitation requires an
  attacker-writable cache directory later read through diskcache pickle loading.

These constraints are locked and visible rather than suppressed. The exit criteria
on each issue require a compatible upstream release, a regenerated lock, rebuilt
images, and a clean audit for that advisory.

## Verification evidence

The following checks were run against the rebuilt images and a disposable fresh
Compose project:

```text
ruff check .
shellcheck --severity=warning scripts/*.sh scripts/lib/*.sh tests/*.sh
python -m pytest tests/ -q -p no:cacheprovider       # 142 passed
docker compose build app mlflow
python -m pip check                                  # both Python images
python -m pip_audit --local                          # only #27 and #28
./scripts/migrate_db.sh --check
python tests/check_dashboard_queries.py              # 18 SQL + 13 Prometheus panels
```

A synthetic stage was written through the application tracker and verified in all
three sinks: PostgreSQL recorded a completed `1/1` lifecycle row and its sample,
MLflow recorded a finished run with run/group/source tags, and Prometheus exposed
request, duration, quality, completion, and expected/recorded sample series for the
same run ID. Grafana provisioned all five dashboards, and its database role could
select those rows but received `permission denied` on insert.

The multi-hour Phi-3 download/fine-tune/evaluation pipeline and a physical NVIDIA GPU
run were not executed during this review. Model repositories were pinned to immutable
revisions, imports and container integration were exercised, and the remaining
model/GPU path should be checked on the target hardware before publishing benchmark
claims.

The supplied Claude artifact URL exposed only an authenticated shell to this
environment; its payload could not be retrieved through the public endpoint. It was
therefore not treated as reviewed evidence. A pasted or exported copy can be appended
to this review in a follow-up.
