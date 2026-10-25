"""Bound context to the model window."""
from __future__ import annotations


def bound(prompt: str, context_tokens: int, reserve_out: int = 256) -> str:
    budget_chars = max(256, (context_tokens - reserve_out)) * 4
    if len(prompt) <= budget_chars:
        return prompt
    return prompt[:budget_chars // 2] + "\n…[truncated]…\n" + prompt[-budget_chars // 2:]
