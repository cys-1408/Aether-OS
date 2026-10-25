"""nftables backend library (used by the AetherOS firewall service).

All execution is list-argv with bounded timeouts. When the caller is not
root, nftables changes go through the documented polkit helper
``/usr/libexec/aether/aether-firewall-helper`` invoked with ``pkexec``
(polkit action ``org.aether.firewall.apply``).
"""
from __future__ import annotations

import logging
import os
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
_AETHER_CORE = REPO_ROOT / "libraries" / "libaether-core" / "python"
if str(_AETHER_CORE) not in sys.path:
    sys.path.insert(0, str(_AETHER_CORE))
_CM_DIR = Path(__file__).resolve().parents[1] / "connection-manager"
if str(_CM_DIR) not in sys.path:
    sys.path.insert(0, str(_CM_DIR))

from _nm import require_tool, run_text, tool_path  # noqa: E402  (connection-manager helpers)

LOG = logging.getLogger(__name__)

HELPER_PATH = "/usr/libexec/aether/aether-firewall-helper"
AETHER_TABLE = "aether_filter"
ALLOWED_RULESET_DIRS = ("/etc/aether/firewall/", "/run/aether/firewall/")

_CHAIN_HEADER_RE = re.compile(r"^\s*chain (\S+) \{")


class FirewallBackendError(RuntimeError):
    pass


def _is_root() -> bool:
    return hasattr(os, "geteuid") and os.geteuid() == 0


def _run_nft(argv: list[str], timeout_s: float) -> tuple[int, str, str]:
    """Run nft directly as root, or through the polkit helper otherwise."""
    require_tool("nft", "nftables userspace tool is required")
    if _is_root():
        return run_text(["nft"] + argv, timeout=timeout_s)
    require_tool("pkexec", "polkit is required for non-root firewall changes")
    if not os.path.isfile(HELPER_PATH):
        raise FirewallBackendError(f"polkit helper not installed at {HELPER_PATH}")
    return run_text(["pkexec", HELPER_PATH] + argv, timeout=timeout_s)


class NftBackend:
    """Thin, honest wrapper around the system nftables state."""

    def available(self) -> bool:
        return tool_path("nft") is not None

    def version(self) -> str | None:
        if not self.available():
            return None
        rc, out, _err = run_text(["nft", "--version"], timeout=5.0)
        if rc != 0:
            return None
        return out.strip().split()[-1] if out.strip() else None

    # -- reading -------------------------------------------------------------
    def list_ruleset_text(self, timeout_s: float = 15.0) -> str:
        """Return raw ``nft list ruleset`` output (may be empty when nothing loaded)."""
        if _is_root():
            rc, out, err = run_text(["nft", "list", "ruleset"], timeout=timeout_s)
        else:
            require_tool("pkexec", "polkit is required for non-root firewall reads")
            if not os.path.isfile(HELPER_PATH):
                raise FirewallBackendError(f"polkit helper not installed at {HELPER_PATH}")
            rc, out, err = run_text(["pkexec", HELPER_PATH, "list"], timeout=timeout_s)
        if rc != 0:
            raise FirewallBackendError(err.strip() or f"nft list ruleset exited rc={rc}")
        return out

    def apply_file(self, path: Path | str, timeout_s: float = 30.0) -> dict:
        """Apply an .nft file; only whitelisted directories are accepted."""
        real = Path(path).resolve()
        allowed = any(str(real).startswith(d) for d in ALLOWED_RULESET_DIRS)
        if not allowed or not real.is_file():
            raise FirewallBackendError(
                f"refusing to apply {real}: must be an existing .nft under "
                + " or ".join(ALLOWED_RULESET_DIRS)
            )
        rc, out, err = _run_nft(["-f", str(real)], timeout_s)
        if rc != 0:
            raise FirewallBackendError(err.strip() or out.strip() or f"nft -f exited rc={rc}")
        return {"applied": True, "source": str(real)}

    def table_exists(self, table: str, family: str = "inet") -> bool:
        ruleset = self.list_ruleset_text()
        inside_family = False
        for line in ruleset.splitlines():
            stripped = line.strip()
            fam_match = re.match(r"^table (\S+) (\S+) \{", stripped)
            if fam_match:
                inside_family = fam_match.group(1) == family and fam_match.group(2) == table
                continue
            if stripped == "}" :
                inside_family = False
            elif inside_family and stripped.startswith("chain"):
                return True
        return False

    def parse_ruleset(self, ruleset_text: str) -> list[dict]:
        """Parse ``nft list ruleset`` output into a structural dict tree."""
        tables: list[dict] = []
        stack: list[dict] = []
        for raw_line in ruleset.splitlines():
            stripped = raw_line.strip()
            if not stripped:
                continue
            table_m = re.match(r"^table (\S+) (\S+) \{$", stripped)
            chain_m = re.match(r"^chain (\S+) \{$", stripped)
            base_m = re.match(
                r"^type (\S+) hook (\S+) priority (\S+)(?:;| policy (\S+);)?\s*$", stripped)
            if table_m:
                table = {"family": table_m.group(1), "name": table_m.group(2),
                         "chains": [], "flags": []}
                tables.append(table)
                stack = [table]
                continue
            if chain_m and tables:
                chain: dict = {"name": chain_m.group(1), "type": None, "hook": None,
                               "policy": None, "rules": []}
                tables[-1]["chains"].append(chain)
                stack = [tables[-1], chain]
                continue
            if base_m and len(stack) >= 2:
                chain = stack[1]
                chain["type"] = base_m.group(1)
                chain["hook"] = base_m.group(2)
                chain["priority"] = base_m.group(3)
                if base_m.group(4):
                    chain["policy"] = base_m.group(4).rstrip(";")
                continue
            if stripped.startswith("}"):
                if stack:
                    stack.pop()
                continue
            if tables and stack and len(stack) >= 2:
                rule = stripped.rstrip(";")
                if rule.startswith("flags"):
                    stack[1].setdefault("flags", []).append(rule)
                elif not rule.startswith(("meta", "type")) or True:
                    stack[1]["rules"].append(rule)
        for table in tables:
            table.pop("flags", None)
        return tables
