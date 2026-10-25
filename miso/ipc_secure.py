"""Authenticated JSON-RPC 2.0 IPC for Miso system services.

``aether_core.ipc.JsonRpcServer`` dispatches handlers with params only, but the
broker, ledger and workspace services MUST identify the peer process
(SO_PEERCRED + systemd unit) before acting on a request. This module implements
the identical wire protocol (JSON-RPC 2.0 envelope, error codes, clean shutdown
on SIGTERM/SIGINT, socket file removal) with per-connection peer credentials:

    handler(params: dict, peer: dict) -> dict
    peer = {"pid", "uid", "gid", "username", "unit"}

Framing: one JSON-RPC request frame per connection. The frame is a single JSON
object; a trailing newline is optional. The server writes one JSON response
object (with trailing newline) and closes the connection. Miso's own client
(:func:`call_auth`) follows the same convention; for interoperability the
server also accepts clients that simply send one JSON document and keep the
connection open (it replies after a short idle period).

Handler errors: raise ``aether_core.errors.IpcError`` (or any AetherError); the
server maps its ``jsonrpc_code`` attribute (default -32000) onto the JSON-RPC
error frame.
"""

from __future__ import annotations

import grp
import json
import logging
import os
import signal
import socket
import threading
from pathlib import Path

from aether_core.errors import AetherError, IpcError
from aether_core.ipc import call as aether_call  # noqa: F401  (interop re-export)

from miso.peercreds import enrich_peer, get_peer_credentials

LOG = logging.getLogger("miso.ipc")

PARSE_ERROR = -32700
INVALID_REQUEST = -32600
METHOD_NOT_FOUND = -32601
INVALID_PARAMS = -32602
INTERNAL_ERROR = -32603

MAX_FRAME_BYTES = 8 * 1024 * 1024
_IDLE_REPLY_SECONDS = 0.4


def ipc_error(message: str, *, jsonrpc_code: int = -32000, code: str = "ipc_error",
              details=None) -> IpcError:
    """Construct an IpcError defensively across AetherError signatures."""
    try:
        exc = IpcError(code, message, details=details)
    except TypeError:
        try:
            exc = IpcError(message)
        except Exception as inner:  # pragma: no cover - signature fallback
            raise AetherError(code, message, details=details) from inner
    existing = getattr(exc, "jsonrpc_code", None)
    if not isinstance(existing, int):
        try:
            exc.jsonrpc_code = jsonrpc_code
        except Exception:
            pass
    return exc


class AuthJsonRpcServer:
    """JSON-RPC 2.0 over UDS with SO_PEERCRED peer identification."""

    def __init__(self, socket_path: Path, methods: dict[str, callable], *,
                 socket_mode: int = 0o660, socket_group: str | None = None,
                 max_frame_bytes: int = MAX_FRAME_BYTES):
        self.socket_path = Path(socket_path)
        self.methods = dict(methods)
        self.socket_mode = socket_mode
        self.socket_group = socket_group
        self.max_frame_bytes = max_frame_bytes
        self._sock: socket.socket | None = None
        self._running = False
        self._stop_lock = threading.Lock()

    # ------------------------------------------------------------- lifecycle
    def serve_forever(self) -> None:
        """Blocking serve loop; SIGTERM/SIGINT stop cleanly and remove the socket."""
        self._prepare_socket()
        signal.signal(signal.SIGTERM, self._on_signal)
        signal.signal(signal.SIGINT, self._on_signal)
        self._running = True
        LOG.info("serving on %s (%d methods)", self.socket_path, len(self.methods))
        while self._running:
            try:
                conn, _ = self._sock.accept()
            except socket.timeout:
                continue
            except OSError:
                if self._running:
                    LOG.exception("accept failed")
                break
            threading.Thread(target=self._serve_connection, args=(conn,),
                             daemon=True, name="miso-ipc-conn").start()
        self._cleanup_socket()

    def stop(self) -> None:
        """Request a clean stop (idempotent)."""
        with self._stop_lock:
            self._running = False
            if self._sock is not None:
                try:
                    self._sock.close()
                except OSError:
                    pass
                self._sock = None
            self._cleanup_socket()

    def _on_signal(self, signum, _frame) -> None:
        LOG.info("signal %s received, stopping", signum)
        self.stop()

    def _prepare_socket(self) -> None:
        self.socket_path.parent.mkdir(parents=True, exist_ok=True)
        try:
            self.socket_path.unlink()
        except FileNotFoundError:
            pass
        previous_umask = os.umask(0o117)
        try:
            sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            sock.bind(str(self.socket_path))
        finally:
            os.umask(previous_umask)
        os.chmod(self.socket_path, self.socket_mode)
        if self.socket_group:
            try:
                gid = grp.getgrnam(self.socket_group).gr_gid
                os.chown(self.socket_path, -1, gid)
            except KeyError:
                LOG.warning("socket group %s does not exist; leaving default",
                            self.socket_group)
        sock.listen(64)
        sock.settimeout(1.0)
        self._sock = sock

    def _cleanup_socket(self) -> None:
        try:
            if self.socket_path.exists():
                self.socket_path.unlink()
        except OSError:
            pass

    # ------------------------------------------------------------- serving
    def _serve_connection(self, conn: socket.socket) -> None:
        peer = {}
        try:
            peer = enrich_peer(get_peer_credentials(conn))
        except OSError:
            peer = {"pid": -1, "uid": -1, "gid": -1, "username": None, "unit": None}
        try:
            with conn:
                conn.settimeout(1.0)
                frame_bytes = self._read_frame(conn)
                if frame_bytes is None:
                    return
                response = self._handle_frame(frame_bytes, peer)
                conn.sendall((json.dumps(response) + "\n").encode("utf-8"))
        except (ConnectionError, BrokenPipeError, socket.timeout):
            pass
        except Exception:
            LOG.exception("connection handler crashed (peer=%s)", peer)

    def _read_frame(self, conn: socket.socket) -> bytes | None:
        """Read one JSON frame: newline-delimited, or a lone document (idle/EOF)."""
        buf = bytearray()
        idle_budget = _IDLE_REPLY_SECONDS
        while True:
            try:
                chunk = conn.recv(65536)
            except socket.timeout:
                if buf:
                    idle_budget -= 1.0
                    if idle_budget <= 0:
                        return bytes(buf)
                    continue
                return None
            if not chunk:
                return bytes(buf) if buf else None
            buf.extend(chunk)
            if b"\n" in buf:
                return bytes(buf.split(b"\n", 1)[0])
            if len(buf) > self.max_frame_bytes:
                return None

    def _handle_frame(self, frame_bytes: bytes, peer: dict) -> dict:
        try:
            frame = json.loads(frame_bytes.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            return self._error_frame(None, PARSE_ERROR, f"parse error: {exc}")
        if not isinstance(frame, dict) or frame.get("jsonrpc") != "2.0" \
                or not isinstance(frame.get("method"), str):
            return self._error_frame(frame.get("id") if isinstance(frame, dict) else None,
                                     INVALID_REQUEST, "not a JSON-RPC 2.0 request frame")
        request_id = frame.get("id")
        handler = self.methods.get(frame["method"])
        if handler is None:
            return self._error_frame(request_id, METHOD_NOT_FOUND,
                                     f"unknown method {frame['method']}")
        params = frame.get("params")
        if params is None:
            params = {}
        if not isinstance(params, dict):
            return self._error_frame(request_id, INVALID_PARAMS, "params must be an object")
        try:
            result = handler(params, peer)
        except AetherError as exc:
            code = getattr(exc, "jsonrpc_code", None)
            if not isinstance(code, int):
                code = -32000
            details = getattr(exc, "details", None)
            return self._error_frame(request_id, code, exc.message, details)
        except Exception as exc:  # noqa: BLE001 - top-level handler guard
            LOG.exception("handler for %s failed (peer=%s)", frame["method"], peer)
            return self._error_frame(request_id, INTERNAL_ERROR,
                                     f"internal error: {exc}")
        if not isinstance(result, dict):
            result = {"value": result}
        return {"jsonrpc": "2.0", "id": request_id, "result": result}

    @staticmethod
    def _error_frame(request_id, code: int, message: str, details=None) -> dict:
        error = {"code": code, "message": message}
        if details is not None:
            error["data"] = details
        return {"jsonrpc": "2.0", "id": request_id, "error": error}


class _Seq:
    _n = 0

    @classmethod
    def next(cls) -> int:
        cls._n += 1
        return cls._n


def call_auth(socket_path: Path, method: str, params: dict | None = None, *,
              timeout: float = 10.0) -> dict:
    """Miso-side JSON-RPC client for AuthJsonRpcServer services.

    Returns the ``result`` object; raises IpcError on error frames.
    """
    frame = {"jsonrpc": "2.0", "id": _Seq.next(), "method": method,
             "params": params if params is not None else {}}
    payload = (json.dumps(frame) + "\n").encode("utf-8")
    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as sock:
        sock.settimeout(timeout)
        sock.connect(str(socket_path))
        sock.sendall(payload)
        buf = bytearray()
        while b"\n" not in buf:
            chunk = sock.recv(65536)
            if not chunk:
                break
            buf.extend(chunk)
            if len(buf) > MAX_FRAME_BYTES:
                raise ipc_error("response too large", jsonrpc_code=-32700,
                                code="response_too_large")
    if not buf:
        raise ipc_error("empty response from service", code="empty_response")
    try:
        reply = json.loads(bytes(buf).decode("utf-8").splitlines()[0])
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ipc_error(f"malformed response frame: {exc}", code="bad_response") from exc
    if "error" in reply and isinstance(reply["error"], dict):
        err = reply["error"]
        raise ipc_error(str(err.get("message", "service error")),
                        jsonrpc_code=int(err.get("code", -32000)),
                        code="service_error", details=err.get("data"))
    if "result" not in reply:
        raise ipc_error("response frame lacks result", code="bad_response")
    return reply["result"]
