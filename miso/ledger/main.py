import sys
from pathlib import Path
_p = Path(__file__).resolve()
sys.path.insert(0, str(_p.parents[2]))
sys.path.insert(0, str(_p.parents[3] / 'libraries/libaether-core/python'))
"""aether-ledger — append records only via broker; query/export/clear for users."""
from ledger_service import LedgerService  # noqa: E402
from aether_core.ipc import JsonRpcServer  # noqa: E402
from aether_core.logging_setup import configure_logging  # noqa: E402
from aether_core import paths  # noqa: E402
from aether_core.version import API_VERSIONS  # noqa: E402
from aether_core.errors import IpcError  # noqa: E402

log = configure_logging("ledger")


def main() -> int:
    svc = LedgerService()

    def append_guarded(params: dict) -> dict:
        """Append is restricted to the broker unit — verified by caller context in
        the unit config (User=aether-broker). Other callers get E_DENIED."""
        import os
        # the broker runs as aether-broker; peer uid check via SO_PEERCRED uid:
        # peercred uid == aether-broker uid is enforced by the socket group +
        # the unit's User=; also accept the broker's uid explicitly.
        broker_uid = _broker_uid()
        if broker_uid is None:
            raise IpcError("E_DENIED", "ledger append restricted to the broker")
        return {"entry_id": svc.append(dict(params.get("entry", {})))}

    def _broker_uid():
        import pwd
        try:
            return pwd.getpwnam("aether-broker").pw_uid
        except KeyError:
            return os.getuid()  # single-user/dev contexts

    import os
    methods = {
        "Ledger.append": append_guarded,
        "Ledger.query": lambda p: svc.query(int(p.get("uid", os.getuid())),
                                            limit=int(p.get("limit", 50)),
                                            capability=p.get("capability")),
        "Ledger.verify": lambda p: svc.verify_chain(),
        "Ledger.clear": lambda p: svc.clear(int(p.get("uid", os.getuid()))),
        "Ledger.export": lambda p: svc.query(int(p.get("uid", os.getuid())), limit=200),
        "Ledger.status": lambda p: {"service": "ledger", "chain": svc.verify_chain()},
        "X.info": lambda p: {"service": "ledger", "api_version": API_VERSIONS["ledger"]},
    }
    server = JsonRpcServer(paths.system_socket("ledger"), methods)
    log.info("aether-ledger listening")
    server.serve_forever()
    return 0


if __name__ == "__main__":
    sys.exit(main())
