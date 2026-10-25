"""GPU probe (see profiler._accelerators) — reuse for focused queries."""
from profiler import _accelerators  # noqa: F401


def gpus() -> list[dict]:
    return _accelerators()
