"""Model memory estimate: weights + KV cache + overhead (LABELED ESTIMATE)."""
from __future__ import annotations


def estimate_model_memory_mb(model: dict, context_len: int = 2048) -> dict:
    """weights + kv_cache + runtime overhead + safety margin.

    KV cache ≈ 2 (K&V) × n_layers × n_head_kv × head_dim × ctx × bytes.
    When GGUF metadata is unavailable (download not yet done), approximate from
    quantization class and size with documented assumptions.
    """
    size_gb = float(model.get("approx_size_gb") or 1.0)
    weights_mb = size_gb * 1024
    quant = (model.get("quantization") or "q4").lower()
    bytes_per = 0.5 if "q4" in quant else 0.75 if "q5" in quant else 1.0 if "q8" in quant else 2.0
    n_layers, n_head_kv, head_dim = _guess_geometry(size_gb)
    kv_mb = 2 * n_layers * n_head_kv * head_dim * context_len * bytes_per / (1024 * 1024)
    overhead_mb = 400
    safety_mb = 500
    total = weights_mb + kv_mb + overhead_mb + safety_mb
    return {"min": int(total * 0.9), "max": int(total * 1.25),
            "breakdown": {"weights_mb": int(weights_mb), "kv_cache_mb": int(kv_mb),
                          "overhead_mb": overhead_mb, "safety_mb": safety_mb},
            "assumed_geometry": {"n_layers": n_layers, "n_head_kv": n_head_kv, "head_dim": head_dim}}


def _guess_geometry(size_gb: float) -> tuple[int, int, int]:
    """Rough public-model geometry by size class (documented assumption)."""
    if size_gb <= 0.5:
        return 16, 6, 64      # ~360M class
    if size_gb <= 1.5:
        return 24, 8, 64      # ~1-1.5B class
    if size_gb <= 3.5:
        return 32, 8, 128     # ~3B class
    if size_gb <= 8.0:
        return 32, 8, 128     # ~7-8B class
    return 40, 8, 128
