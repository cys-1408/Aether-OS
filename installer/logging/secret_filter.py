"""Passphrase/token scrubbing for any logged line."""
from __future__ import annotations

import re


def scrub(text: str) -> str:
    return re.sub(r"(?i)(passphrase|password|token)\s*[=:]\s*\S+", r"\1=[REDACTED]", text or "")
