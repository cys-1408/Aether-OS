"""GPU offload when an accelerator AND a GPU-capable build are present."""
from __future__ import annotations

import subprocess

from cpu_backend_adapter import spawn_options


def supports_gpu(binary: str) -> bool:
    try:
        out = subprocess.run([binary, "--version"], capture_output=True, text=True, timeout=10)
        text = (out.stdout + out.stderr).lower()
        return any(k in text for k in ("cuda", "vulkan", "rocm", "metal"))
    except (OSError, subprocess.TimeoutExpired):
        return False


def spawn_options_with_offload(binary: str, model_path: str, ctx: int, port: int, gpu_ok: bool) -> list[str]:
    argv = [binary]
    argv += spawn_options(model_path, ctx, port)
    if gpu_ok and supports_gpu(binary):
        argv += ["-ngl", "999"]
    return argv
