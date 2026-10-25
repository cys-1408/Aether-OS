"""Task budgets from miso.yaml."""
from __future__ import annotations


def budgets(config: dict) -> dict:
    b = config.get("budgets", {})
    return {"max_steps": int(b.get("max_steps", 8)),
            "max_duration_s": int(b.get("max_duration_s", 120)),
            "max_tokens": int(b.get("max_tokens", 4000))}
