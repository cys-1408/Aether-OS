"""UDS bridge for Software Center (socket 'packages')."""
from __future__ import annotations

import sys
from pathlib import Path

_p = Path(__file__).resolve()
sys.path.insert(0, str(_p.parents[2] / "libraries/libaether-core/python"))
sys.path.insert(0, str(_p.parents[1]))

from aether_core.ipc import JsonRpcServer  # noqa: E402
from aether_core import paths  # noqa: E402
from core.package_manager import search, installed, info, install, remove, update_all, history  # noqa: E402


def main() -> int:
    methods = {
        "Packages.search": lambda p: {"packages": search(str(p.get("query", "")))},
        "Packages.installed": lambda p: {"packages": installed()},
        "Packages.info": lambda p: info(str(p.get("name", ""))),
        "Packages.install": lambda p: install(list(p.get("packages", []))),
        "Packages.remove": lambda p: remove(list(p.get("packages", []))),
        "Packages.update": lambda p: update_all(),
        "Packages.history": lambda p: {"history": history()},
    }
    server = JsonRpcServer(paths.system_socket("packages"), methods)
    server.serve_forever()
    return 0


if __name__ == "__main__":
    sys.exit(main())
