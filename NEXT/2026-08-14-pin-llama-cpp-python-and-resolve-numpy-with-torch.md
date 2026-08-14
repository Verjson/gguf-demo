---
date: 2026-08-14
issue:
title: Pin llama-cpp-python and resolve numpy in the same transaction as torch
---

`llama-cpp-python` was installed unpinned from `https://abetlen.github.io/...` over
`--extra-index-url`, so every rebuild took whatever that index had published most recently,
unreviewed and unverified. It is now pinned to `0.3.34` in `Dockerfile.app` (one
`LLAMA_CPP_VERSION` build arg feeding all four install branches) and in both `pyproject.toml`
constraints. The wheel is `py3-none-manylinux2014_x86_64`, present on the cpu and cu124
indexes and on PyPI at that version.

`numpy` moved into the same pip transaction as `torch`, bounded `>=1.26.3,<2` everywhere it
appears. It was previously installed last, as its own transaction, which let it downgrade
underneath an already-installed torch — a build that succeeds and then fails at `import torch`
with a C ABI error, far from the cause.

Still open: the wheels are not hash-pinned, so a compromise of that index remains build-time
code execution, and `--extra-index-url` keeps PyPI in the resolution set. Adding
`--require-hashes` needs a rebuild to confirm the selected wheel, which has not been run.
