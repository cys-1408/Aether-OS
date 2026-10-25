import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "libraries/libaether-core/python"))
"""aether-logs — query + redacted diagnostic bundles."""
from service_main import SystemService  # noqa: E402
from journal_adapter import query  # noqa: E402
from diagnostic_bundle import create  # noqa: E402


def build_service() -> SystemService:
    return SystemService("logs", "logs", {
        "Logs.query": lambda p: query(
            unit=p.get("unit"), since=p.get("since"), until=p.get("until"),
            priority=p.get("priority"), contains=p.get("contains"),
            lines=int(p.get("lines", 200))),
        "Logs.bundle": lambda p: create(list(p.get("scope", [])), bool(p.get("consent", False))),
    })


if __name__ == "__main__":
    build_service().run()
