"""Path-scope safety: where Miso file capabilities may operate.

Approved roots are the user's standard content directories plus the user's
Aether state directory. Well-known sensitive locations (keys, credentials,
policy configuration) are refused even when nested under approved roots, and
system trees are refused outright. All checks operate on realpaths.
"""

from __future__ import annotations

import os
from pathlib import Path

from aether_core.errors import AetherError
from aether_core.filesops import is_within

HOME_SUBDIR_ROOTS = ("Documents", "Downloads", "Pictures", "Music", "Videos", "Desktop")

# Refused even though they sit under $HOME.
SENSITIVE_HOME_PARTS = (
    ".ssh", ".gnupg", ".password-store", ".pki", ".kube", ".aws", ".gnome-keyring",
    ".config/aether", ".local/share/aether/ledger", ".local/share/keyrings",
)

# System trees never approved for user file capabilities.
SYSTEM_DENY_ROOTS = (
    "/etc", "/usr", "/boot", "/root", "/proc", "/sys", "/dev", "/bin", "/sbin",
    "/lib", "/lib32", "/lib64", "/libx32", "/opt", "/srv", "/var", "/run",
)


def home_for(uid: int) -> Path:
    """Home directory for a uid (falls back to passwd lookup at call time)."""
    import pwd

    try:
        return Path(pwd.getpwuid(uid).pw_dir)
    except KeyError as exc:
        raise AetherError("unknown_uid", f"no passwd entry for uid {uid}") from exc


def approved_roots(uid: int) -> list[Path]:
    """Directories in which file capabilities may operate for this uid."""
    home = home_for(uid)
    roots = [home / sub for sub in HOME_SUBDIR_ROOTS]
    roots.append(home / ".local/share/aether")
    roots.append(home / ".local/share/Trash")
    return roots


def is_sensitive(path: Path) -> bool:
    """True when the path resolves inside a sensitive or system location."""
    resolved = Path(os.path.realpath(str(path)))
    for denied in SYSTEM_DENY_ROOTS:
        if is_within(resolved, Path(denied)):
            return True
    # Compare the sensitive-fragment list against the path's parts.
    parts = "/".join(resolved.parts)
    for fragment in SENSITIVE_HOME_PARTS:
        marker = "/" + fragment
        if marker + "/" in parts or parts.endswith(marker):
            return True
    return False


def classify(path: Path | str, uid: int) -> dict:
    """Classify a path for a uid: {"allowed": bool, "reason": str}."""
    try:
        candidate = Path(os.path.expanduser(str(path)))
        if not candidate.is_absolute():
            return {"allowed": False, "reason": "relative paths are not accepted"}
        resolved = Path(os.path.realpath(str(candidate)))
        if is_sensitive(resolved):
            return {"allowed": False, "reason": f"refusing sensitive/system path {resolved}"}
        for root in approved_roots(uid):
            if is_within(resolved, Path(os.path.realpath(str(root)))):
                return {"allowed": True, "reason": f"within approved root {root}"}
        return {"allowed": False,
                "reason": "path is outside approved roots (home content directories "
                          "and ~/.local/share/aether)"}
    except (OSError, ValueError) as exc:
        return {"allowed": False, "reason": f"cannot resolve path: {exc}"}


def assert_in_scope(path: Path | str, uid: int) -> Path:
    """Raise a scope-violation error unless ``path`` is approved for ``uid``."""
    verdict = classify(path, uid)
    if not verdict["allowed"]:
        raise AetherError("path_out_of_scope",
                          f"path refused by resource scope check: {verdict['reason']}")
    return Path(os.path.realpath(os.path.expanduser(str(path))))
