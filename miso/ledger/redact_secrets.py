"""Pre-insert secret redaction (defense in depth with the safety filter)."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "safety"))
from sensitive_data_filter import redact_params  # noqa: F401
