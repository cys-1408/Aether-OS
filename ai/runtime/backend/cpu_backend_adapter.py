"""CPU-only llama.cpp spawn options."""
from __future__ import annotations

import os


def threads() -> int:
    return max(1, (os.cpu_count() or 2) - 1)


def spawn_options(model_path: str, ctx: int, port: int) -> list[str]:
    return ["-m", model_path, "-c", str(ctx), "--host", "127.0.0.1",
            "--port", str(port), "-t", str(threads())]
