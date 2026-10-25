"""Secret redaction before planner/ledger exposure."""
from __future__ import annotations

import re

PATTERNS = [
    (re.compile(r"(?i)(password|passwd|pwd)\s*[=:]\s*\S+"), "password=[REDACTED]"),
    (re.compile(r"(?i)(token|bearer)\s*[=:]\s*\S+"), "token=[REDACTED]"),
    (re.compile(r"(?i)(api[_-]?key)\s*[=:]\s*\S+"), "api_key=[REDACTED]"),
    (re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----[\s\S]*?-----END [A-Z ]*PRIVATE KEY-----"), "[PRIVATE KEY REDACTED]"),
    (re.compile(r"AKIA[0-9A-Z]{16}"), "[AWS KEY REDACTED]"),
]


def redact_params(obj) -> dict:
    text = obj if isinstance(obj, str) else json.dumps(obj, default=str)
    for pat, repl in PATTERNS:
        text = pat.sub(repl, text)
    return obj if isinstance(obj, str) else json.loads(text)


import json  # noqa: E402
