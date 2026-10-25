import sys
from pathlib import Path
_p = Path(__file__).resolve()
sys.path.insert(0, str(_p.parents[2]))
sys.path.insert(0, str(_p.parents[3] / 'libraries/libaether-core/python'))
"""aether-workspace — save/preview/restore user-approved layouts."""
from workspace_service import WorkspaceService  # noqa: E402
from layout_capture import capture_current  # noqa: E402
from aether_core.ipc import JsonRpcServer  # noqa: E402
from aether_core.logging_setup import configure_logging  # noqa: E402
from aether_core import paths  # noqa: E402
from aether_core.version import API_VERSIONS  # noqa: E402
from aether_core.errors import IpcError  # noqa: E402
import os  # noqa: E402

log = configure_logging("workspace")


def main() -> int:
    svc = WorkspaceService()

    def uid_of(params: dict) -> int:
        return int(params.get("uid", os.getuid()))

    methods = {
        "Workspace.save": lambda p: svc.save(uid_of(p), str(p.get("name", "")),
                                             dict(p.get("layout") or capture_current())),
        "Workspace.list": lambda p: svc.list(uid_of(p)),
        "Workspace.preview_restore": lambda p: svc.preview_restore(uid_of(p), str(p.get("workspace_id", ""))),
        "Workspace.restore": lambda p: svc.restore(uid_of(p), str(p.get("workspace_id", "")),
                                                   bool(p.get("confirmed", False))),
        "Workspace.delete": lambda p: svc.delete(uid_of(p), str(p.get("workspace_id", ""))),
        "X.info": lambda p: {"service": "workspace", "api_version": API_VERSIONS["workspace"]},
    }
    server = JsonRpcServer(paths.system_socket("workspace"), methods)
    log.info("aether-workspace listening")
    server.serve_forever()
    return 0


if __name__ == "__main__":
    sys.exit(main())
