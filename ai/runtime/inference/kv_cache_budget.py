"""KV cache budget enforcement (from memory_estimator geometry)."""
from __future__ import annotations


def max_context_for_budget(budget_mb: int, weights_mb: int, overhead_mb: int = 900) -> int:
    """Solve ctx ≈ (budget - weights - overhead) / per-token-cost."""
    free_mb = max(0, budget_mb - weights_mb - overhead_mb)
    # per-token K+V for a 1.5B-class model @q8: ~0.06 MB/token (documented approximation)
    per_token_mb = 0.06
    return max(512, int(free_mb / per_token_mb))
