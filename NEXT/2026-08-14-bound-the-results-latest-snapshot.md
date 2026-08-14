---
date: 2026-08-14
issue:
title: Bound the results/latest snapshot so it cannot copy the repo into itself
---

`scripts/09_compare_runtimes.py` passed the repo root to `refresh_latest()`, which
`shutil.copytree`'d `/app` into `/app/results/latest`. Because `results/` is bind-mounted to
the host and the destination lives inside the source, each run copied the 17GB Hugging Face
cache plus every previous copy of `results/` back onto the host disk. Six runs nested six
levels deep and wrote roughly 100GB of real duplicated files, filling the WSL2 VHDX and
deadlocking the distro with `Wsl/Service/E_UNEXPECTED`.

The call site now passes the comparison folder it just wrote, and `refresh_latest()` enforces
its invariants rather than trusting them. The destination must be a `results/latest/`
directory, checked before anything is removed: with only the containment check, transposing
the arguments — `refresh_latest(run_dir, repo_root)` — passed and then `rmtree`'d the repo,
deleting `src/`, `scripts/` and the bind-mounted `results/` before failing. It also refuses a
source that contains the destination, refuses a source *inside* the destination (clearing it
would delete the source it is about to read), and no longer removes the destination directory
at all: it unlinks the artifact types it writes, so a mistargeted destination loses at most
files of those types. What it copies is an allowlist of flat text artifacts (`.csv`, `.json`,
`.jsonl`, `.md`, `.txt`, `.yaml`, `.yml`), each under 64MB and 256MB in total, instead of a
directory tree — so a cache, subdirectory, or model weight file can no longer ride along, and
everything skipped is logged with the reason. When the total cap does bite, it sheds in a
deliberate order: `manifest.json` and `summary.md` first, then the files the README links, then
the rest — alphabetical order dropped the run's identity while keeping per-question bulk that
nothing could then attribute.

Symlinks in the destination are removed unconditionally, and each artifact is written to a
fresh temp file that is renamed into place. `results/` is a container-writable bind mount, so a
symlink planted there was an arbitrary host write: the previous clear step deliberately
preserved symlinks and the copy then followed one, overwriting whatever it pointed at outside
`results/` with snapshot content.

Whatever the clear step leaves — directories, and files that are not artifact types — is now
named at WARNING. Leaving them is the policy that stops a mistargeted destination from being
destroyed, but leaving them silently was a dead end: a `results/latest/results/` directory
survives every refresh and then aborts the pipeline at startup, so nothing in the tooling was
saying that only a human deleting it resolves that state. `HOME` moves off `/app` to
`/tmp/home` so stray dotfile caches cannot land beside the bind mount; `HF_HOME` stays on the
`huggingface_cache` named volume.

`scripts/run_pipeline.sh` fails loudly instead of silently doubling: it aborts at startup,
after each export, and after each comparison step if any `results/*/results` exists or
`results/` exceeds `RESULTS_MAX_MB` (default 5000). A `results/` that exists but cannot be
measured is a hard failure too — falling through as "fine" would wave past exactly the
runaway growth the guard exists to catch, at the moment the tree is too broken to walk. `results/latest/` is now gitignored — it
is a regenerated copy of the newest `results/runs/<run_id>/`, which stays committed.
