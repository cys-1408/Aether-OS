"""Broker core: the ONLY route from agent intent to real actions (fail closed)."""
from __future__ import annotations

import time

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "capability-os/registry"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "policy-engine"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "safety"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "capabilities"))

from capability_registry import load_registry  # noqa: E402
from policy_engine import PolicyEngine  # noqa: E402
from rate_limiter import RateLimiter  # noqa: E402
from idempotency_store import IdempotencyStore  # noqa: E402
from execution_dispatcher import dispatch  # noqa: E402
from result_verification import verify  # noqa: E402
from broker_audit_hooks import ledger_entry  # noqa: E402
from aether_core.errors import IpcError  # noqa: E402


class BrokerService:
    def __init__(self, config: dict):
        self.config = config
        self.registry = load_registry()
        self.policy = PolicyEngine()
        self.rate = RateLimiter()
        self.idem = IdempotencyStore()
        if not self.policy.integrity_ok():
            raise RuntimeError("policy integrity check failed at startup — refusing to start")

    def request(self, req: dict, peer_uid: int) -> dict:
        entry = ledger_entry({"status": "received", "request": req})
        try:
            return self._handle(req, peer_uid, entry)
        except IpcError as e:
            ledger_entry({"status": "denied", "request": req, "error": e.code})
            return {"request_id": req.get("request_id", "?"), "outcome": "denied",
                    "error": {"code": e.code, "message": e.message, "retriable": e.retriable},
                    "reasons": [e.message]}

    def _handle(self, req: dict, peer_uid: int, entry) -> dict:
        rid = req.get("request_id") or ""
        if self.idem.seen(rid):
            return {"request_id": rid, "outcome": "ok", "result": self.idem.result_of(rid),
                    "reasons": ["idempotent replay"]}
        cap = self.registry.get(req.get("capability_id", ""))
        if not cap:
            raise IpcError("E_UNKNOWN_CAPABILITY", f"capability {req.get('capability_id')!r} not registered")
        # identity: agent requests must come from the same user
        if req.get("requester", {}).get("kind") == "agent" and req["requester"].get("uid") != peer_uid:
            raise IpcError("E_IDENTITY", "agent request uid mismatch")
        # schema validation
        from schema_validation import validate_params
        validate_params(cap, req.get("params", {}))
        # resource scope
        from resource_scope_check import check_scope
        check_scope(cap, req.get("params", {}))
        # rate limit
        if not self.rate.allow(peer_uid, cap["id"]):
            raise IpcError("E_RATE", "capability rate limit exceeded", retriable=True)
        # policy decision (fail closed if integrity broke mid-flight)
        if not self.policy.integrity_ok():
            raise IpcError("E_POLICY_TAMPER", "policy files changed — failing closed")
        decision = self.policy.decide(cap, req.get("requester", {}), req.get("params", {}))
        if decision["decision"] == "deny":
            raise IpcError("E_DENIED", "; ".join(decision["reasons"]))
        if decision["decision"] == "confirm" and not req.get("confirmation_token"):
            ledger_entry({"status": "needs_confirmation", "request": req, "decision": decision})
            return {"request_id": req.get("request_id", "?"), "outcome": "needs_confirmation",
                    "reasons": decision["reasons"], "decision": decision}
        # execute
        result = dispatch(cap, req.get("params", {}), peer_uid)
        verified = verify(cap, result)
        entry_out = ledger_entry({"status": "executed", "request": req, "result": result,
                                  "verified": verified, "decision": decision})
        self.idem.store(rid, result)
        return {"request_id": req.get("request_id", "?"), "outcome": "ok", "result": result,
                "verification": verified, "ledger_entry_id": entry_out,
                "undo": cap.get("undo", {"supported": False}),
                "reasons": decision["reasons"]}

    def capabilities(self) -> dict:
        return {"capabilities": [{"id": cid, "risk_class": c["risk_class"],
                                  "provider": c["provider"],
                                  "confirmation": c["confirmation"]}
                                 for cid, c in sorted(self.registry.items())]}

    def status(self) -> dict:
        return {"service": "broker", "capabilities": len(self.registry),
                "policy_integrity": self.policy.integrity_ok()}
