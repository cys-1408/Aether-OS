"""Typed success/failure results used consistently across services."""


def ok(value):
    """Success envelope: {"ok": True, "value": value}."""
    return {"ok": True, "value": value}


def err(code: str, message: str, *, retriable: bool = False, details=None):
    """Failure envelope: {"ok": False, "error": {...}}."""
    return {
        "ok": False,
        "error": {"code": code, "message": message, "retriable": retriable, "details": details},
    }
