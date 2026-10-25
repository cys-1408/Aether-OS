"""Agent loop bounds."""
from __future__ import annotations

from aether_core.errors import IpcError

MAX_STEPS = 8
MAX_ITERATIONS = 12


def check_step(index: int) -> None:
    if index > MAX_STEPS:
        raise IpcError("E_BUDGET", f"plan exceeded {MAX_STEPS} steps")


def check_iteration(i: int) -> None:
    if i > MAX_ITERATIONS:
        raise IpcError("E_BUDGET", f"loop exceeded {MAX_ITERATIONS} iterations")
