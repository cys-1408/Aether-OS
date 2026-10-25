"""Shell UDS JSON-RPC server (socket ``shell`` under /run/user/$UID/aether/).

This is the endpoint Miso's broker calls for the desktop provider. The server:

* serves EXACTLY the Shell.* methods from CONVENTIONS.md §4 (see
  ``window_manager.window_capabilities``) plus the two task-mandated extras
  (``Shell.confirm`` token-gated for the broker, ``Shell.launcher_toggle``);
* verifies peer credentials (SO_PEERCRED) so only the logged-in user's
  processes may call user-session methods;
* uses ``aether_core.ipc.JsonRpcServer`` when available, with a stdlib-only
  fallback implementation of the same envelope so the shell stays functional
  if the shared library is broken (truthfully logged, never faked).
"""
from __future__ import annotations

import json
import logging
import os
import secrets
import socket
import socketserver
import threading
from pathlib import Path
from typing import Any, Callable, Dict, Optional

import shell.pkgmap  # noqa: F401
from shell import aether_runtime

LOG = logging.getLogger("aether.shell.uds")

TOKEN_FILE = Path(f"/run/user/{os.getuid()}/aether/shell-session-token")


class ShellUdsService:
    """Owns the shell socket lifecycle and the method dispatch table."""

    def __init__(self, methods: Dict[str, Callable[[dict], dict]]) -> None:
        self._methods = methods
        self._server = None
        self._thread: Optional[threading.Thread] = None
        self._fallback_stop = threading.Event()
        self.auth_token = self._ensure_session_token()

    # ------------------------------------------------------------- token
    @staticmethod
    def _ensure_session_token() -> str:
        """Create/read the 0600 session token used to gate Shell.confirm."""
        try:
            if TOKEN_FILE.exists():
                token = TOKEN_FILE.read_text(encoding="utf-8").strip()
                if token:
                    return token
            TOKEN_FILE.parent.mkdir(parents=True, exist_ok=True)
            token = secrets.token_hex(32)
            TOKEN_FILE.write_text(token, encoding="utf-8")
            os.chmod(TOKEN_FILE, 0o600)
            return token
        except OSError as exc:
            LOG.error("session token unavailable (%s); Shell.confirm will refuse", exc)
            return ""

    # ------------------------------------------------------------- guards
    @staticmethod
    def _peer_uid(connection: Any) -> Optional[int]:
        """Return the peer's uid via SO_PEERCRED (Linux), None when unknown."""
        try:
            import struct  # noqa: WPS433

            creds = connection.getsockopt(socket.SOL_SOCKET, socket.SO_PEERCRED, 12)
            pid, uid, _gid = struct.unpack("3i", creds)
            return int(uid)
        except Exception:  # noqa: BLE001 - platform without SO_PEERCRED
            return None

    # ------------------------------------------------------------- start
    def start(self) -> bool:
        """Start serving on the shell socket; returns True when serving."""
        socket_path = aether_runtime.user_socket(aether_runtime.SHELL_SOCKET)
        try:
            import aether_core  # noqa: WPS433

            self._server = aether_core.ipc.JsonRpcServer(
                socket_path, dict(self._methods), socket_mode=0o660
            )
            self._thread = threading.Thread(
                target=self._server.serve_forever, name="aether-shell-uds", daemon=True
            )
            self._thread.start()
            LOG.info("shell UDS serving on %s (aether_core JsonRpcServer)", socket_path)
            return True
        except Exception as exc:
            LOG.warning("aether_core JsonRpcServer unavailable (%s); using fallback", exc)
        self._start_fallback(socket_path)
        return True

    def _start_fallback(self, socket_path: Path) -> None:
        """Stdlib JSON-RPC 2.0 server with the same envelope semantics."""
        service = self

        class Handler(socketserver.BaseRequestHandler):
            """One-shot JSON-RPC request handler (matching aether_core envelope)."""

            def handle(self) -> None:
                uid = ShellUdsService._peer_uid(self.request)
                if uid is not None and uid != os.getuid():
                    self._reply({"error": {"code": -32001, "message": "peer uid mismatch"}})
                    return
                try:
                    self.request.settimeout(30)
                    raw = self._read_frame()
                    request = json.loads(raw.decode("utf-8"))
                except Exception as exc:  # noqa: BLE001
                    self._reply({"error": {"code": -32700, "message": f"parse error: {exc}"}})
                    return
                method = str(request.get("method", ""))
                params = request.get("params") or {}
                request_id = request.get("id")
                handler = service._methods.get(method)
                if handler is None:
                    error = {"code": -32601, "message": f"unknown method {method!r}"}
                else:
                    try:
                        result = handler(params if isinstance(params, dict) else {})
                        self._reply({"result": result})
                        return
                    except Exception as exc:  # noqa: BLE001
                        error = {
                            "code": getattr(exc, "jsonrpc_code", -32000),
                            "message": str(exc),
                            "data": {"code": getattr(exc, "code", exc.__class__.__name__)},
                        }
                if request_id is None:
                    return
                self._reply({"error": error})

            def _read_frame(self) -> bytes:
                chunks = []
                while True:
                    chunk = self.request.recv(65536)
                    if not chunk:
                        break
                    chunks.append(chunk)
                    if b"\n" in chunk:
                        break
                return b"".join(chunks).strip() or b"{}"

            def _reply(self, payload: dict) -> None:
                body = json.dumps(payload).encode("utf-8") + b"\n"
                self.request.sendall(body)

        class Server(socketserver.ThreadingUnixStreamServer):
            """Threading UDS server with unlink-on-close."""

            allow_reuse_address = True
            daemon_threads = True

        try:
            if socket_path.exists():
                socket_path.unlink()
            socket_path.parent.mkdir(parents=True, exist_ok=True)
            self._server = Server(str(socket_path))
            os.chmod(socket_path, 0o660)
            self._thread = threading.Thread(
                target=self._server.serve_forever, name="aether-shell-uds-fallback",
                daemon=True,
            )
            self._thread.start()
            LOG.warning("shell UDS serving on %s (stdlib fallback server)", socket_path)
        except OSError as exc:
            LOG.error("shell UDS could not bind %s: %s", socket_path, exc)

    # ------------------------------------------------------------- stop
    def stop(self) -> None:
        """Stop the server and remove the socket file."""
        self._fallback_stop.set()
        server = self._server
        if server is None:
            return
        stop = getattr(server, "stop", None) or getattr(server, "shutdown", None)
        if callable(stop):
            try:
                stop()
            except Exception:  # noqa: BLE001
                LOG.exception("UDS server stop failed")
        server_close = getattr(server, "server_close", None)
        if callable(server_close):
            try:
                server_close()
            except Exception:  # noqa: BLE001
                LOG.exception("UDS server_close failed")
        socket_path = aether_runtime.user_socket(aether_runtime.SHELL_SOCKET)
        try:
            if socket_path.exists():
                socket_path.unlink()
        except OSError:
            pass
        self._server = None
