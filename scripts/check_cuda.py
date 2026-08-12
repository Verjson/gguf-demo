#!/usr/bin/env python3
"""
CUDA smoke test for WSL2 + Docker + NVIDIA GPU setups.

Run inside the app container after `docker compose up -d`:
  docker compose exec app python scripts/check_cuda.py

Checks:
  1. PyTorch sees CUDA
  2. GPU name / driver / capability
  3. A tiny tensor matmul on GPU (when available)
  4. hardware.py summary (same path used by evaluation scripts)
"""

from __future__ import annotations

import shutil
import subprocess
import sys

sys.path.insert(0, "/app")

import torch

from src.hardware import detect_hardware


def run_nvidia_smi() -> str | None:
    """Return nvidia-smi output if the utility exists in the container."""
    if not shutil.which("nvidia-smi"):
        return None
    try:
        result = subprocess.run(
            ["nvidia-smi", "--query-gpu=name,driver_version,memory.total", "--format=csv,noheader"],
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except Exception:  # noqa: BLE001
        pass
    return None


def gpu_matmul_smoke() -> tuple[bool, float, str]:
    """Run a small matmul on GPU; return (ok, seconds, message)."""
    if not torch.cuda.is_available():
        return False, 0.0, "Skipped — CUDA not available"

    import time

    try:
        device = torch.device("cuda:0")
        a = torch.randn(512, 512, device=device)
        b = torch.randn(512, 512, device=device)
        torch.cuda.synchronize()
        start = time.perf_counter()
        _ = a @ b
        torch.cuda.synchronize()
        elapsed = time.perf_counter() - start
        return True, elapsed, f"512x512 matmul OK in {elapsed * 1000:.1f} ms"
    except Exception as exc:  # noqa: BLE001
        return False, 0.0, f"GPU matmul failed: {exc}"


def main() -> None:
    print("=" * 72)
    print("CUDA SMOKE TEST (gguf-demo app container)")
    print("=" * 72)

    # --- Layer 1: nvidia-smi (optional inside container) ---
    smi = run_nvidia_smi()
    if smi:
        print("\n[nvidia-smi]")
        for line in smi.splitlines():
            print(f"  {line}")
    else:
        print("\n[nvidia-smi] not found in container (OK — PyTorch check matters more)")

    # --- Layer 2: PyTorch / hardware.py ---
    info = detect_hardware()
    print("\n[PyTorch / hardware]")
    print(f"  {info.summary()}")
    print(f"  torch version     : {info.torch_version}")
    print(f"  torch cuda build  : {info.cuda_version or 'none (CPU wheel?)'}")
    print(f"  cuda.is_available : {torch.cuda.is_available()}")
    print(f"  device_count      : {torch.cuda.device_count()}")

    if torch.cuda.is_available():
        print(f"  current device    : {torch.cuda.current_device()}")
        props = torch.cuda.get_device_properties(0)
        print(f"  total memory      : {props.total_memory / 1024**3:.1f} GiB")

    # --- Layer 3: compute smoke test ---
    ok, elapsed, msg = gpu_matmul_smoke()
    print("\n[GPU compute smoke test]")
    print(f"  {msg}")

    # --- Verdict ---
    print("\n" + "=" * 72)
    if info.cuda_available and ok:
        print("PASS — CUDA is available and GPU compute works.")
        print("Evaluation scripts will log cuda_used=1.0 and device=cuda.")
    elif info.cuda_available and not ok:
        print("PARTIAL — CUDA detected but compute failed.")
        print("Check driver / Docker GPU passthrough (gpus: all in compose).")
        sys.exit(1)
    else:
        print("CPU MODE — CUDA not available inside this container.")
        print("Fix checklist (WSL2 + Windows laptop):")
        print("  1. Windows: NVIDIA driver with WSL support (nvidia-smi works in WSL)")
        print("  2. Docker Desktop: Settings → Resources → enable GPU")
        print("     OR WSL: install nvidia-container-toolkit + restart docker")
        print("  3. Rebuild app with cu118 torch:")
        print("     TORCH_INDEX_URL=https://download.pytorch.org/whl/cu118 docker compose build app")
        print("  4. Recreate container: docker compose up -d --force-recreate app")
        print("  5. Re-run: docker compose exec app python scripts/check_cuda.py")
        sys.exit(1)

    print("=" * 72)


if __name__ == "__main__":
    main()
