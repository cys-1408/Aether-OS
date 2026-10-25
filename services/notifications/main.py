import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "libraries/libaether-core/python"))
"""aether-notification — real notifications with policy + rate limits."""
from service_main import SystemService  # noqa: E402
import notification_service as ns  # noqa: E402
from notification_policy import category_enabled  # noqa: E402
from notification_rate_limit import allow  # noqa: E402


def _notify_checked(params: dict) -> dict:
    category = str(params.get("category", "system"))
    if not category_enabled(category).get("enabled", True):
        return {"suppressed": True, "reason": f"category {category} disabled by policy"}
    gate = allow(category, str(params.get("key", params.get("title", ""))))
    if not gate.get("allowed"):
        return {"suppressed": True, "reason": "rate limited", "retry_in_s": gate.get("retry_in_s")}
    return ns.notify(str(params.get("source", "system")), category,
                     str(params.get("title", "")), str(params.get("body", "")))


def build_service() -> SystemService:
    return SystemService("notifications", "notifications", {
        "Notify.notify": _notify_checked,
        "Notify.list": lambda p: ns.list_notifications(bool(p.get("unread_only", False))),
        "Notify.close": lambda p: ns.close(str(p.get("id", ""))),
        "Notify.history": lambda p: ns.history(int(p.get("limit", 50))),
    })


if __name__ == "__main__":
    build_service().run()
