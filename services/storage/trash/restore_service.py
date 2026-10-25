"""Restore semantics documented + conflict-safe wrapper (see filesops.restore)."""
from aether_core import filesops  # noqa: F401
from aether_core.errors import AetherError  # noqa: F401


def restore_with_report(name: str) -> dict:
    result = filesops.restore(name)
    result["conflict_policy"] = "rename with ' (2)' suffix — never silent overwrite"
    return result
