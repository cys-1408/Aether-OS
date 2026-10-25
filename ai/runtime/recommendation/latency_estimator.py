"""Grounded latency estimate with uncertainty — never a guarantee."""
from __future__ import annotations


def estimate_latency(model: dict, gpu_ok: bool) -> dict:
    """Bandwidth-bound decode: tok/s ≈ 0.7 × effective_BW / weights_GB."""
    size_gb = float(model.get("approx_size_gb") or 1.0)
    bw_gbps = 120.0 if gpu_ok else 25.0   # conservative DDR4/VRAM band assumptions
    tok_s = 0.7 * bw_gbps / max(size_gb, 0.1)
    return {"tokens_per_s_estimate": round(tok_s, 1),
            "uncertainty": "±50%", "gpu_offload": gpu_ok,
            "note": "ESTIMATE only — measured tok/s reported after validation smoke check"}
