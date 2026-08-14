---
date: 2026-08-14
issue:
title: Size the run to the machine it lands on, not the machine it can see
---

Cap thread pools by the CPU budget the container is actually granted (cgroup quota or cpuset), evaluate one sample at a time so a single local model is not contended by ten concurrent requests, and read memory limits from cgroups so the numbers hold when the pipeline itself runs in a container. Together these took CPU throttling from 80% of scheduling periods to near zero.
