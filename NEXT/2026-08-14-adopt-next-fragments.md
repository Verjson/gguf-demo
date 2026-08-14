---
date: 2026-08-14
issue:
title: Replace NEXT.md with a NEXT/ fragment directory
---

A single shared changelog file makes every concurrent pull request conflict on that one file. `NEXT/` holds one file per entry, which never collides, and `scripts/render-next.sh` assembles them newest-first for reading. Existing entries were migrated with the commit dates that introduced them.

The standing design note on CPU decode moved to `docs/cpu-decode-ceiling.md`: it documents a property of the workload rather than a change, so it does not belong in a changelog.
