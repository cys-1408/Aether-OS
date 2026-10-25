"""journald-friendly structured logging + secret redaction."""
from __future__ import annotations

import json
import logging
import os
import re
import sys
from pathlib import Path

_REDACT_PATTERNS = [
    re.compile(r"(?i)(password|passwd|pwd)\s*[=:]\s*\S+"),
    re.compile(r"(?i)(token|bearer)\s*[=:]\s*\S+"),
    re.compile(r"(?i)(api[_-]?key|apikey)\s*[=:]\s*\S+"),
    re.compile(r"(?i)authorization\s*:\s*\S+"),
    re.compile(r"-----BEGIN (RSA |EC |OPENSSH )?PRIVATE KEY-----"),
]
_REPLACEMENT = "[REDACTED]"
_configured: set[str] = set()


def configure_logging(service: str, level: str = "INFO") -> logging.Logger:
    """Configure a journald-friendly logger (plain stderr lines)."""
    logger = logging.getLogger(f"aether-{service}")
    if service in _configured:
        return logger
    handler = logging.StreamHandler(sys.stderr)
    if os.environ.get("AETHER_LOG_JSON") == "1":
        class JsonFormatter(logging.Formatter):
            def format(self, record):
                return json.dumps({
                    "ts": self.formatTime(record, "%Y-%m-%dT%H:%M:%S%z"),
                    "service": service, "level": record.levelname,
                    "msg": record.getMessage(),
                })
        handler.setFormatter(JsonFormatter())
    else:
        handler.setFormatter(logging.Formatter(f"aether-{service}: %(levelname)s %(message)s"))
    logger.addHandler(handler)
    logger.setLevel(getattr(logging, level.upper(), logging.INFO))
    logger.propagate = False
    _configured.add(service)
    return logger


def redact_text(text: str, rules_path: Path | str | None = None) -> str:
    """Redact credential-looking values. rules_path may extend defaults."""
    out = text
    for pat in _REDACT_PATTERNS:
        out = pat.sub(lambda m: m.group(0).split("=")[0].split(":")[0] + "=" + _REPLACEMENT, out)
    if rules_path:
        try:
            import yaml
            rules = yaml.safe_load(Path(rules_path).read_text()) or {}
            replacement = rules.get("replacement", _REPLACEMENT)
            for rule in rules.get("patterns", []):
                try:
                    out = re.sub(rule["regex"], replacement, out)
                except re.error:
                    continue
        except Exception:
            pass
    return out
