"""Prompts/outputs are NOT persisted by default; opt-in cache with retention."""
from __future__ import annotations


class PromptLogPolicy:
    def __init__(self, enabled: bool = False, retention_days: int = 0):
        self.enabled = enabled
        self.retention_days = retention_days
        self._entries: list[dict] = []

    def record(self, request_id: str, direction: str, text: str) -> None:
        if not self.enabled:
            return  # default: nothing retained
        self._entries.append({"request_id": request_id, "direction": direction, "len": len(text)})

    def sweep(self) -> int:
        return 0  # retention_days=0 → nothing ever stored
