"""Shared helpers for file capabilities: param validation, conflicts, scope.

All file operations go through :mod:`miso.safety.path_scope` (approved roots,
sensitive-location refusal) and use argv-only subprocess where a helper program
is needed. Conflict handling follows a small explicit policy: rename (default),
overwrite, skip.
"""

from __future__ import annotations

import os
import shutil
from pathlib import Path

from aether_core.errors import AetherError

CONFLICT_POLICIES = ("rename", "overwrite", "skip")


def require_path(params: dict, ctx: dict | None = None, key: str = "path") -> Path:
    """Extract and scope-check a path parameter for the requesting uid."""
    raw = params.get(key)
    if not isinstance(raw, str) or not raw.strip():
        raise AetherError("missing_param", f"{key} is required and must be a string")
    from miso.safety.path_scope import assert_in_scope

    return assert_in_scope(raw, scope_uid(ctx))


def scope_uid(ctx: dict | None = None) -> int:
    """Scope uid for the current execution context.

    Preference order: ctx["uid"] (requester uid provided by the broker) > the
    MISO_SCOPE_UID environment variable set by the privilege-dropping child
    runner > the current real uid (co-located development runs).
    """
    if isinstance(ctx, dict) and isinstance(ctx.get("uid"), int):
        return int(ctx["uid"])
    env_uid = os.environ.get("MISO_SCOPE_UID")
    if env_uid and env_uid.isdigit():
        return int(env_uid)
    return os.getuid()


def require_existing(path: Path) -> Path:
    """Ensure a scoped path exists (file or directory)."""
    if not path.exists():
        raise AetherError("target_missing", f"no such file or directory: {path}")
    return path


def unique_destination(destination: Path) -> Path:
    """Append " (2)", " (3)" ... before the suffix until the name is free."""
    if not destination.exists():
        return destination
    stem, suffix = destination.stem, destination.suffix
    parent = destination.parent
    counter = 2
    while True:
        candidate = parent / f"{stem} ({counter}){suffix}"
        if not candidate.exists():
            return candidate
        counter += 1


def resolve_conflict(destination: Path, policy: str) -> tuple[Path, str] | None:
    """Apply the conflict policy; returns (target, resolution) or None to skip."""
    if policy not in CONFLICT_POLICIES:
        raise AetherError("invalid_params",
                          f"conflict must be one of {CONFLICT_POLICIES}")
    if not destination.exists():
        return destination, "none"
    if policy == "skip":
        return None
    if policy == "overwrite":
        return destination, "overwritten"
    return unique_destination(destination), "renamed"


def snapshot(path: Path) -> dict:
    """Stat snapshot used for honest undo bookkeeping."""
    try:
        stat = path.stat()
        return {"path": str(path), "size": stat.st_size, "exists": True,
                "mtime_ns": stat.st_mtime_ns}
    except OSError:
        return {"path": str(path), "exists": False}


def same_file(a: Path, b: Path) -> bool:
    """True when both paths refer to the same inode (or the same file)."""
    try:
        return os.path.samefile(a, b)
    except OSError:
        return False


def copy_with_fallback(source: Path, destination: Path) -> int:
    """Copy a file, falling back to copytree semantics for directories."""
    if source.is_dir():
        shutil.copytree(source, destination)
        return sum(1 for _ in destination.rglob("*"))
    shutil.copy2(source, destination)
    return destination.stat().st_size
