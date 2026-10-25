"""Redaction loader over redaction-rules.yaml (see aether_core.logging_setup)."""
from __future__ import annotations

from pathlib import Path

from aether_core.logging_setup import redact_text

RULES = Path("/etc/aether") / "redaction-rules.yaml"


def redact(text: str) -> str:
    return redact_text(text, rules_path=RULES)
