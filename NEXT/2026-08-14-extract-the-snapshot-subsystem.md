---
date: 2026-08-14
issue:
title: Extract the results/latest snapshot subsystem into its own module
---

`src/run_results.py` was 766 lines covering two unrelated jobs: what a run produced, and
how `results/latest/` is refreshed. The second is where every host-safety invariant lives —
containment in both directions, the destination-shape check, symlink handling, the size
caps — and it read as a digression inside an export helper.

`src/snapshot.py` now owns it (300 lines), `run_results.py` is 490, and the seam is clean:
snapshot depends on nothing above it, so `run_results` imports `refresh_latest` rather than
the reverse. The nine snapshot tests moved to `tests/test_snapshot.py`, whose docstring
describes what they actually cover; the file they left no longer claims to test
README-as-summary.

Pure move — no logic changed.
