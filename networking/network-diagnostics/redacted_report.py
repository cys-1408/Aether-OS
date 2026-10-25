"""Redacted diagnostic reports for AetherOS networking.

``build_report`` assembles section payloads; IP addresses and MAC addresses
are stripped unless the caller passes ``keep_ips=True`` together with
``consent=True``.  The default (and any non-consented call) always redacts.
"""
from __future__ import annotations

import copy
import datetime as _dt
import re

_IPV4_RE = re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b")
_IPV6_RE = re.compile(r"\b(?:[0-9A-Fa-f]{1,4}:){2,7}[0-9A-Fa-f]{1,4}\b")
_MAC_RE = re.compile(r"\b(?:[0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}\b")


def _redact_text(text: str) -> str:
    text = _MAC_RE.sub("<mac-redacted>", text)
    text = _IPV4_RE.sub("<ip-redacted>", text)
    text = _IPV6_RE.sub("<ip-redacted>", text)
    return text


def redact_structure(value, keep_ips: bool = False):
    """Recursively redact IP/MAC strings inside dicts, lists and strings."""
    if keep_ips:
        return value
    if isinstance(value, str):
        return _redact_text(value)
    if isinstance(value, dict):
        return {k: redact_structure(v, keep_ips) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [redact_structure(v, keep_ips) for v in value]
    return value


def build_report(sections: dict, *, keep_ips: bool = False, consent: bool = False,
                 title: str = "network diagnostics") -> dict:
    """Build a report; requires explicit consent to keep addresses unredacted.

    Raises ValueError when ``keep_ips=True`` is requested without consent.
    """
    if keep_ips and not consent:
        raise ValueError("keeping IP addresses requires explicit user consent (consent=True)")
    report = {
        "title": title,
        "generated_at": _dt.datetime.now(_dt.timezone.utc).isoformat(),
        "addresses_redacted": not keep_ips,
        "sections": {},
    }
    for name, payload in sections.items():
        report["sections"][name] = copy.deepcopy(payload)
    report["sections"] = redact_structure(report["sections"], keep_ips)
    return report
