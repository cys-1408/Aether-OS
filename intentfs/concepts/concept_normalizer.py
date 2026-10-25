"""Normalize concepts: trim, lowercase, dedupe, clamp length."""
from __future__ import annotations

import re


def normalize(concepts: list) -> list[str]:
    out = []
    for c in concepts:
        if not isinstance(c, str):
            continue
        c = re.sub(r"\s+", " ", c.strip().lower())
        c = re.sub(r"[^a-z0-9 \-]", "", c)
        c = c[:32].strip()
        if len(c) >= 2 and c not in out:
            out.append(c)
    return out
