---
date: 2026-08-14
issue:
title: Migrate to the langchain v1 line and drop two unused dependencies
---

Renovate opened ten dependency PRs against two mutually exclusive langchain tracks, and an
earlier merge had already left `pyproject.toml` unsatisfiable: `langchain>=0.3.30` requires
`langchain-core>=0.3.85`, while this project pinned `<0.2`. pip refused the pair outright.

Nothing in this codebase imports `langchain` — only `langchain-core`, `langchain-community`
and `langchain-text-splitters` — so the umbrella is gone rather than upgraded, which
dissolves the conflict. `ragas` was declared in both dependency lists and imported nowhere;
it is gone too.

`langchain-community` 0.4 requires `langchain-core>=1.4`, so the family moves to the v1 line
together. community is sunset upstream, and the two integrations that moved out now come
from their standalone packages: `langchain-huggingface` for `HuggingFaceEmbeddings`,
`langchain-postgres` for `PGVector`. That store speaks psycopg 3, so the SQLAlchemy URL
changes to `postgresql+psycopg://` and `psycopg[binary]` joins psycopg2, which still serves
the direct metrics writes. The constructor keywords changed with it —
`connection_string`/`embedding_function` became `connection`/`embeddings`.

`transformers` moves to 4.57. The Phi-3 SDPA workaround silently stopped working there:
4.48 removed `PHI3_ATTENTION_CLASSES`, so the probe returned False on a version where SDPA
is native *and* the default, and the loader stopped asking for it explicitly. It now asks
the model class what it supports, keeping the old patch only for versions that need it.

pyproject and Dockerfile.app declare these dependencies twice, which is how the drift went
unseen. `tests/test_dependency_parity.py` now fails when they disagree — it caught a numpy
bound that existed in the image but not in pyproject.
