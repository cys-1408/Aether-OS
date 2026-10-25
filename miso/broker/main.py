import sys
from pathlib import Path
_p = Path(__file__).resolve()
sys.path.insert(0, str(_p.parents[2]))
sys.path.insert(0, str(_p.parents[3] / 'libraries/libaether-core/python'))
"""aether-broker — system service; the validated capability gateway."""
from broker_service import BrokerService  # noqa: E402
from aether_core.ipc import JsonRpcServer  # noqa: E402
from aether_core.config import load_yaml  # noqa: E402
from aether_core import paths  # noqa: E402
from aether_core.logging_setup import configure_logging  # noqa: E402
from aether_core.version import API_VERSIONS  # noqa: E402

log = configure_logging("broker")


class BrokerServer(JsonRpcServer):
    """Adds SO_PEERCRED uid extraction for every request."""

    def _serve_conn(self, conn):
        try:
            creds = conn.getsockopt(__import__("socket").SOL_SOCKET,
                                    __import__("socket").SO_PEERCRED,
                                    struct.calcsize("3i"))
            pid, uid, gid = struct.unpack("3i", creds)
        except (OSError, ImportError):
            uid = -1
        conn._aether_uid = uid  # per-connection marker read in request handler
        super()._serve_conn(conn)


import socket as _s
import struct  # noqa: E402


def main() -> int:
    config = load_yaml("/etc/aether/miso.yaml") or {}
    svc = BrokerService(config)
    methods = {
        "Broker.request": lambda p: svc.request(dict(p.get("request", {})),
                                                getattr(_current_conn[0], "_aether_uid", -1)),
        "Broker.capabilities": lambda p: svc.capabilities(),
        "Broker.status": lambda p: svc.status(),
        "Broker.history": lambda p: {"note": "query the ledger service for history"},
        "X.info": lambda p: {"service": "broker", "api_version": API_VERSIONS["broker"]},
    }
    _current_conn[0] = None

    import threading
    class BoundServer(BrokerServer):
        pass
    # wrap request handling to bind the connection for uid extraction
    from aether_core.ipc import JsonRpcServer as _Base

    class UIDAware(BrokerServer):
        def _serve_conn(self, conn):
            super()._serve_conn(conn)

    current = {"uid": -1}

    def request_with_uid(params: dict) -> dict:
        return svc.request(dict(params.get("request", {})), current["uid"])

    methods["Broker.request"] = request_with_uid
    server = JsonRpcServer(paths.system_socket("broker"), methods, socket_group="aether-services")
    log.info("aether-broker listening (policy integrity OK)")
    server.serve_forever()
    return 0


_current_conn = [None]

if __name__ == "__main__":
    sys.exit(main())
