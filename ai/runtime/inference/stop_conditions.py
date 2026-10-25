"""Stop conditions: token cap, timeout, stop strings, cancellation."""
from __future__ import annotations

import time


class StopConditions:
    def __init__(self, max_tokens: int, timeout_s: float, stop: list[str], token):
        self.max_tokens = max_tokens
        self.deadline = time.monotonic() + timeout_s
        self.stop = stop or []
        self.token = token

    def should_stop(self, generated_tokens: int, text: str) -> tuple[bool, str]:
        import time as _t
        if self.token and self.token.cancelled():
            return True, "cancelled"
        if _t.monotonic() > self.deadline:
            return True, "timeout"
        if generated_tokens >= self.max_tokens:
            return True, "token_cap"
        for s in self.stop:
            if s and s in text:
                return True, "stop_string"
        return False, ""
