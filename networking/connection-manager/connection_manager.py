"""Connection-profile manager (library used by the AetherOS network-service).

Stores reusable network profiles as YAML files under
``~/.config/aether/network-profiles/`` (override with the
``AETHER_NETWORK_PROFILES`` environment variable), validated against
``connection_profiles.schema.json`` living next to this module.

Profiles are user intent records ("connect to this SSID with these DNS
servers"); the actual activation always happens through NetworkManager.
"""
from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
_AETHER_CORE = REPO_ROOT / "libraries" / "libaether-core" / "python"
if str(_AETHER_CORE) not in sys.path:
    sys.path.insert(0, str(_AETHER_CORE))

from aether_core.config import atomic_write_yaml, load_yaml  # noqa: E402
from aether_core.errors import AetherError  # noqa: E402
from aether_core.schema import validate  # noqa: E402

SCHEMA_PATH = Path(__file__).resolve().parent / "connection_profiles.schema.json"
PROFILE_NAME_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9 ._-]{0,63}$")


class ProfileError(RuntimeError):
    pass


def profile_dir() -> Path:
    override = os.environ.get("AETHER_NETWORK_PROFILES")
    if override:
        return Path(override)
    from aether_core.paths import USER_CONFIG_DIR
    return Path(USER_CONFIG_DIR) / "network-profiles"


def load_schema() -> dict:
    with SCHEMA_PATH.open("r", encoding="utf-8") as fh:
        return json.load(fh)


class ConnectionManager:
    """Read/write/validate AetherOS network profiles."""

    def __init__(self, directory: Path | None = None) -> None:
        self._dir = Path(directory) if directory else profile_dir()
        self._schema = load_schema()

    # -- validation ---------------------------------------------------------
    def validate(self, profile: dict) -> None:
        try:
            validate(profile, self._schema)
        except AetherError as exc:
            raise ProfileError(f"profile validation failed: {exc.message}") from exc
        name = profile.get("name", "")
        if not PROFILE_NAME_RE.match(name):
            raise ProfileError("profile name must match [A-Za-z0-9][A-Za-z0-9 ._-]{0,63}")
        for dns in profile.get("dns_servers", []) or []:
            import ipaddress
            try:
                ipaddress.ip_address(dns)
            except ValueError as exc:
                raise ProfileError(f"invalid DNS server '{dns}'") from exc

    # -- CRUD ----------------------------------------------------------------
    def list_profiles(self) -> list[dict]:
        if not self._dir.is_dir():
            return []
        out: list[dict] = []
        for path in sorted(self._dir.glob("*.yaml")):
            try:
                out.append(load_yaml(path))
            except (OSError, ValueError) as exc:
                out.append({"name": path.stem, "invalid": True, "error": str(exc)})
        return out

    def load_profile(self, name: str) -> dict:
        self._check_name(name)
        path = self._dir / f"{name}.yaml"
        if not path.is_file():
            raise ProfileError(f"profile '{name}' does not exist")
        profile = load_yaml(path)
        self.validate(profile)
        return profile

    def save_profile(self, profile: dict) -> Path:
        self.validate(profile)
        self._dir.mkdir(parents=True, exist_ok=True)
        path = self._dir / f"{profile['name']}.yaml"
        atomic_write_yaml(path, profile)
        return path

    def delete_profile(self, name: str) -> bool:
        self._check_name(name)
        path = self._dir / f"{name}.yaml"
        if not path.is_file():
            return False
        path.unlink()
        return True

    # -- helpers -------------------------------------------------------------
    def to_nmcli_dns_args(self, profile: dict) -> list[str]:
        """Render a profile's DNS servers as nmcli connection modify arguments."""
        servers = profile.get("dns_servers") or []
        if not servers:
            return []
        return ["ipv4.dns", " ".join(servers)]

    def dhcp_policy(self) -> dict:
        """Load the bundled DHCP client policy (validated, with sane defaults)."""
        policy_path = Path(__file__).resolve().parent / "dhcp_client_policy.yaml"
        try:
            policy = load_yaml(policy_path)
        except (OSError, ValueError):
            policy = {}
        defaults = {
            "client": "networkmanager",
            "request_timeout_s": 30,
            "require_dhcp_server_validation": False,
            "allowed_lease_time_range": [300, 86400],
        }
        defaults.update(policy if isinstance(policy, dict) else {})
        lo, hi = defaults["allowed_lease_time_range"]
        if not (isinstance(lo, int) and isinstance(hi, int) and 0 < lo <= hi):
            defaults["allowed_lease_time_range"] = [300, 86400]
        return defaults

    @staticmethod
    def _check_name(name: str) -> None:
        if not isinstance(name, str) or not PROFILE_NAME_RE.match(name):
            raise ProfileError("invalid profile name")
