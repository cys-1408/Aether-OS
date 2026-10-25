"""Active connection summary."""
from network_service import general_status, get_dns, vpn_status  # noqa: F401


def summary() -> dict:
    return {"general": general_status(), "dns": get_dns(), "vpn": vpn_status()}
