---
date: 2026-08-14
issue:
title: Size the app's memory cap from Docker, not from the host
---

On macOS the app container was killed on model load. `available_memory_bytes()` read `/proc/meminfo`, which does not exist there, so it fell through to a 10g default — while Docker Desktop's VM was smaller than that, and the container was killed for exceeding a limit the VM could never honor.

The number that matters is what Docker can actually give a container. `docker info` reports it on every platform: on Linux it equals the host's RAM (verified: 23.46 GiB both ways), and on macOS and Windows it is the VM, which is the thing that fills up. The host reading is now only a fallback for when Docker cannot be queried, with `sysctl hw.memsize` covering Darwin, and a cgroup limit still wins when the pipeline itself runs in a container. The low-memory warning now also says where to change it on Docker Desktop, since raising the VM is the actual fix there.

`scripts/host_guard.sh` had the same `/proc/meminfo` assumption and would have exited immediately on a Mac. It now falls back to measuring container usage against the Docker VM's size — the budget containers are actually killed for exceeding — and reports which source it used. `GUARD_MEM_SOURCE` forces either path, which is how the Docker path is exercised on a Linux box that has `/proc`.
