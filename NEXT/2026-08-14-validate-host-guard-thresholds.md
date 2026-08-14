---
date: 2026-08-14
issue:
title: Validate host_guard thresholds before they reach awk
---

`scripts/host_guard.sh` interpolated `--warn-pct`, `--critical-pct`, `--swap-warn-pct`,
`--swap-critical-pct`, `--heartbeat-every` and `--interval` straight into an awk program body.
A value that is valid awk in that position executed on the first sample: `--critical-pct
'0 || system("touch /tmp/pwned") || 0'` ran the command, verified against the pre-fix script.

Each numeric flag is now checked against `^[0-9]+$` at parse time and the script exits 2
otherwise, so a non-integer never reaches awk; the comparisons pass their values with `awk -v`,
making the program text fixed. `--heartbeat-every` and `--interval` additionally require at
least 1 (the first divides, the second would spin the sampler), and `--log` must resolve under
the repository or a temp directory. `tests/test_host_guard.sh` covers the injection shape for
all four threshold flags, the numeric and range rejections, the log-path rejection, and that a
valid invocation still samples, emits, and writes its log.

Nothing invokes this watchdog yet, so this lands before it is wired into the pipeline rather
than after.
