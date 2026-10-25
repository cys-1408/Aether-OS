"""Reject incompatible models BEFORE download."""
from __future__ import annotations


def filter_compatible(model: dict, profile: dict, budget_mb: int) -> dict:
    reasons = []
    if model.get("format", "gguf") != "gguf":
        reasons.append("only gguf supported by current backend")
    mem_min = float(model.get("min_ram_gb", 0)) * 1024
    if mem_min and mem_min > (profile.get("memory", {}).get("total_mb") or 0):
        reasons.append(f"needs {model.get('min_ram_gb')}GB RAM")
    if budget_mb and float(model.get("approx_size_gb") or 0) * 1024 * 1.4 > budget_mb:
        reasons.append("estimated memory exceeds inference budget")
    if not model.get("license"):
        reasons.append("license unknown — refuse")
    return {"compatible": not reasons, "reasons": reasons}
