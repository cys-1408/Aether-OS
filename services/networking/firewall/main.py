import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "libraries/libaether-core/python"))
"""aether-firewall — nftables-backed policy service."""
from service_main import SystemService  # noqa: E402
import firewall_policy, rule_manager, policy_validation  # noqa: E402


def build_service() -> SystemService:
    return SystemService("firewall", "firewall", {
        "Firewall.status": lambda p: firewall_policy.status(),
        "Firewall.list_rules": lambda p: firewall_policy.list_rules(),
        "Firewall.apply_default": lambda p: firewall_policy.apply_default(),
        "Firewall.open_port": lambda p: rule_manager.open_port(int(p.get("port", 0)), str(p.get("protocol", "tcp"))),
        "Firewall.validate_rule": lambda p: policy_validation.validate_rule(dict(p.get("rule", {}))),
    })


if __name__ == "__main__":
    build_service().run()
