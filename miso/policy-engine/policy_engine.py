"""Policy decisions at execution time (fail closed)."""
from __future__ import annotations

from policy_loader import PolicyLoader


class PolicyEngine:
    def __init__(self):
        self.loader = PolicyLoader()

    def decide(self, capability: dict, requester: dict, params: dict) -> dict:
        cid = capability.get("id", "?")
        risk = capability.get("risk_class", "write")
        layers = self.loader.layers()
        for layer in layers:  # most specific first
            for rule in layer.get("overrides", []):
                if rule.get("capability") == cid:
                    effect = rule.get("effect")
                    return {"decision": {"deny": "deny", "allow": "allow", "confirm": "confirm"}.get(effect, "deny"),
                            "reasons": [f"explicit override: {rule.get('reason', '')}"],
                            "applied_policy": layer.get("name", "?")}
        default = layers[0].get("defaults", {}) if layers else {}
        if risk == "destructive":
            return {"decision": "confirm", "reasons": ["destructive requires strong confirmation"],
                    "applied_policy": "destructive-action"}
        effect = {"read_only": default.get("read_only", "allow"),
                  "low_reversible": default.get("low_reversible", "allow"),
                  "write": default.get("write", "confirm")}.get(risk, "confirm")
        return {"decision": effect, "reasons": [f"default policy for {risk}"],
                "applied_policy": "default"}

    def integrity_ok(self) -> bool:
        return self.loader.integrity_ok()
