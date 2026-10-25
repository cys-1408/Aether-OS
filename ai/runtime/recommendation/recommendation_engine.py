"""Rank compatible models for task + machine (facts vs estimates labeled)."""
from __future__ import annotations

from compatibility_filter import filter_compatible
from memory_estimator import estimate_model_memory_mb
from latency_estimator import estimate_latency


def recommend(config: dict, catalog: dict, profile: dict, task_class: str = "assistant") -> dict:
    budget_mb = (profile.get("estimates", {}).get("inference_memory_budget_mb") or 0)
    accel = (profile.get("accelerators") or [None])[0]
    gpu_ok = bool(accel and accel.get("driver"))
    scored = []
    for model in catalog.get("models", []):
        if task_class not in model.get("task_classes", []):
            continue
        verdict = filter_compatible(model, profile, budget_mb)
        if not verdict["compatible"]:
            continue
        mem_est = estimate_model_memory_mb(model, context_len=min(model.get("context_lengths", [2048]) or [2048]))
        lat = estimate_latency(model, gpu_ok)
        scored.append({
            "model_id": model["model_id"], "name": model["name"],
            "repo": model["repo"], "file": model["file"],
            "license": model.get("license"), "approx_size_gb": model.get("approx_size_gb"),
            "memory_estimate_mb": mem_est, "latency_estimate": lat,
            "fit_reasons": verdict["reasons"],
            "estimate_labels": ["memory_estimate_mb is an ESTIMATE", "latency is an ESTIMATE with uncertainty"],
        })
    scored.sort(key=lambda m: m["memory_estimate_mb"]["max"] if m["memory_estimate_mb"] else 0)
    return {"available": True, "task_class": task_class, "budget_mb": budget_mb,
            "recommendations": scored[:3]}
