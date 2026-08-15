---
date: 2026-08-14
issue:
title: Extract the pipeline's host helpers so the tests can call them
---

`scripts/run_pipeline.sh` was 603 lines, about 165 of which were host-facing infrastructure
ahead of the pipeline proper: memory accounting, port probing and publishing, and the
results budget guard. They are now `scripts/lib/host.sh`, sourced by the pipeline.

The payoff is testability rather than tidiness. `assert_results_budget` is arithmetic over a
directory, but reaching it meant a full `run_pipeline.sh` invocation with a fake docker on
PATH. `tests/test_run_pipeline.sh` now sources the library and calls the function directly,
covering both the over-budget rejection and the within-budget pass — verified by mutation:
neutering the comparison makes the test fail.

`tests/test_host_portability.sh` can do the same for the memory and port helpers.
