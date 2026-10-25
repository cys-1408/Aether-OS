"""Risk class + bulk escalation heuristics."""
from __future__ import annotations


def effective_risk(cap: dict, params: dict) -> str:
    risk = cap.get("risk_class", "write")
    if risk == "write" and isinstance(params.get("paths"), list) and len(params["paths"]) > 10:
        return "destructive"  # bulk operations escalate
    return risk
