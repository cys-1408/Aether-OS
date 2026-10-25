import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "libraries/libaether-core/python"))
"""aether-network-service — Wi-Fi/Ethernet/DNS/VPN via NetworkManager."""
from service_main import SystemService  # noqa: E402
import network_service  # noqa: E402
from wifi_adapter import adapter_state  # noqa: E402
from ethernet_adapter import ethernet_state  # noqa: E402


def build_service() -> SystemService:
    return SystemService("network", "network", {
        "Network.status": lambda p: {
            "general": network_service.general_status(),
            "wifi": adapter_state(), "ethernet": ethernet_state(),
            "dns": network_service.get_dns(), "vpn": network_service.vpn_status(),
        },
        "Network.wifi_scan": lambda p: network_service.wifi_scan(),
        "Network.wifi_connect": lambda p: network_service.wifi_connect(
            str(p.get("ssid", "")), str(p.get("password", ""))),
        "Network.wifi_disconnect": lambda p: network_service.wifi_disconnect(str(p.get("ssid", ""))),
        "Network.enable": lambda p: network_service.enable_networking(True),
        "Network.disable": lambda p: network_service.enable_networking(False),
        "Network.wifi_enable": lambda p: network_service.set_wifi_enabled(True),
        "Network.wifi_disable": lambda p: network_service.set_wifi_enabled(False),
        "Network.get_dns": lambda p: network_service.get_dns(),
        "Network.set_dns": lambda p: network_service.set_dns(
            str(p.get("connection", "")), list(p.get("servers", []))),
        "Network.vpn_status": lambda p: network_service.vpn_status(),
    })


if __name__ == "__main__":
    build_service().run()
