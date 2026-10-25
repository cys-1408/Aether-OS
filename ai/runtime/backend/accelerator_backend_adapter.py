"""Accelerator-aware adapter selection (GPU when detected, else CPU)."""
from __future__ import annotations

from gpu_backend_adapter import spawn_options_with_offload, supports_gpu  # noqa: F401
