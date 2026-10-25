"""Shared-memory (iGPU) estimation helpers."""
from __future__ import annotations


def igpu_shared_budget_mb(total_mb: int, cap: int = 4096) -> int:
    """Integrated GPUs share system RAM; cap what inference may use."""
    return min(max(0, total_mb // 2), cap)
