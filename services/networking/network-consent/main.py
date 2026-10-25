import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "libraries/libaether-core/python"))
"""aether-network-consent — capability network egress gate."""
from service_main import SystemService  # noqa: E402
import per_capability_network_policy as policy  # noqa: E402


def build_service() -> SystemService:
    return SystemService("consent", "consent", {
        "Consent.check": lambda p: policy.check(str(p.get("capability_id", "")), str(p.get("data_class", "personal"))),
        "Consent.grant": lambda p: policy.grant(str(p.get("capability_id", ""))),
        "Consent.revoke": lambda p: policy.revoke(str(p.get("capability_id", ""))),
        "Consent.list": lambda p: policy.list_all(),
    })


if __name__ == "__main__":
    build_service().run()
