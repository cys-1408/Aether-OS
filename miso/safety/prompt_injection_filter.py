"""Injection pattern detection + quarantine."""
from __future__ import annotations

import re

PATTERNS = [
    re.compile(r"ignore (all |any |previous |prior )?(instructions|prompts|rules)", re.I),
    re.compile(r"disregard .{0,30}(instructions|policy|rules)", re.I),
    re.compile(r"(run|execute) (the )?(following )?(command|shell|script)", re.I),
    re.compile(r"(delete|remove|format) (all |the )?(files|disk|data)", re.I),
    re.compile(r"disable .{0,20}(policy|broker|audit|ledger)", re.I),
    re.compile(r"you are now|act as|pretend to be", re.I),
]


def is_suspicious(text: str) -> dict:
    hits = [p.pattern for p in PATTERNS if p.search(text or "")]
    return {"suspicious": bool(hits), "patterns": hits[:3]}


def quarantine(text: str) -> str:
    """Strip the content out of any planning context."""
    return "[content quarantined: instruction-like patterns detected]"
