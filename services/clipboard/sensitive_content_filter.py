"""Sensitive clipboard content: excluded from history by pattern."""
from __future__ import annotations

import re

PATTERNS = [
    re.compile(r"(?i)(password|passwd|pwd)\s*[=:]\s*\S+"),
    re.compile(r"(?i)\b(bearer|token)\s+[A-Za-z0-9._-]{16,}"),
    re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    re.compile(r"-----BEGIN (RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    re.compile(r"(?i)\b(sk-[A-Za-z0-9]{20,})\b"),
]


def is_sensitive(text: str) -> bool:
    return any(p.search(text or "") for p in PATTERNS)
