"""User-scoped trash service over aether_core.filesops (XDG spec)."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "libraries/libaether-core/python"))

from service_main import SystemService  # noqa: E402
from aether_core import filesops  # noqa: E402


def build_service() -> SystemService:
    return SystemService("trash", "trash", {
        "Trash.trash": lambda p: filesops.trash(Path(str(p.get("path", ""))).expanduser()),
        "Trash.list": lambda p: {"items": filesops.list_trash()},
        "Trash.restore": lambda p: filesops.restore(str(p.get("name", ""))),
        "Trash.purge": lambda p: filesops.empty_trash_items(list(p.get("names", []))),
        "Trash.size": lambda p: {"bytes": filesops.trash_size()},
    }, socket_group=None)


if __name__ == "__main__":
    build_service().run()
