"""Output validation: non-empty, size-capped, control-char stripped."""
from __future__ import annotations

import re


def validate_output(text: str) -> str:
    cleaned = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f]", "", text or "")
    if not cleaned.strip():
        from aether_core.errors import AetherError
        raise AetherError("E_EMPTY_OUTPUT", "model returned empty output")
    return cleaned[:65536]
