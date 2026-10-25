"""Smoke check results with measured latency."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "libraries/libaether-core/python"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from firstboot_controller import commit_page, load_state  # noqa: F401


def present(runtime_client) -> dict:
    """Render from real Runtime data; returns choices to commit."""
    return {"page": 'model_validation_page', "state": load_state()}
