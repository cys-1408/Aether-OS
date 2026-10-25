"""JSON-RPC 2.0 over unix domain sockets — THE Aether local IPC (v1).

Server: JsonRpcServer(socket_path, methods) — one thread per connection.
Client: call(socket_path, method, params, timeout) -> result dict.
Errors: raise IpcError (or return raw dict handlers may raise AetherError).
"""
from __future__ import annotations

import json
import os
import signal
import socket
import struct
import threading
from pathlib import Path
from typing import Callable

from .errors import AetherError, IpcError
from .version import API_VERSIONS

MAX_FRAME = 32 * 1024 * 1024  # 32 MiB guard


def _recv_exact(conn: socket.socket, n: int) -> bytes:
    buf = b""
    while len(buf) < n:
        chunk = conn.recv(n - len(buf))
        if not chunk:
            raise ConnectionError("peer closed")
        buf += chunk
    return buf


def _read_message(sock: socket.socket) -> dict:
    header = _recv_exact(sock, 4)
    (length,) = struct.unpack(">I", header)
    if length > MAX_FRAME:
        raise IpcError("E_FRAME", "frame too large", jsonrpc_code=-32700)
    return json.loads(_recv_exact(sock, length).decode("utf-8"))


def _write_message(sock: socket.socket, obj: dict) -> None:
    data = json.dumps(obj).encode("utf-8")
    sock.sendall(struct.pack(">I", len(data)) + data)


class JsonRpcServer:
    """Serve `methods` over a unix socket. Methods map name -> callable(dict)->dict."""

    def __init__(self, socket_path: Path | str, methods: dict[str, Callable[[dict], dict]],
                 *, socket_mode: int = 0o660, socket_group: str | None = None):
        self.socket_path = Path(socket_path)
        self.methods = dict(methods)
        self.socket_mode = socket_mode
        self.socket_group = socket_group
        self._sock: socket.socket | None = None
        self._stop = threading.Event()
        self._threads: list[threading.Thread] = []

    # -- lifecycle ---------------------------------------------------------
    def _bind(self) -> socket.socket:
        self.socket_path.parent.mkdir(parents=True, exist_ok=True)
        if self.socket_path.exists():
            self.socket_path.unlink()
        srv = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        srv.bind(str(self.socket_path))
        old = os.umask(0o000)
        try:
            os.chmod(self.socket_path, self.socket_mode)
        finally:
            os.umask(old)
        if self.socket_group:
            import grp
            gid = grp.getgrnam(self.socket_group).gr_gid
            os.chown(self.socket_path, -1, gid)
        srv.listen(64)
        srv.settimeout(0.5)
        return srv

    def serve_forever(self) -> None:
        self._sock = self._bind()
        try:
            signal.signal(signal.SIGTERM, self._handle_signal)
            signal.signal(signal.SIGINT, self._handle_signal)
        except ValueError:
            # Not in the main thread (e.g. embedded/in-process use): rely on stop().
            pass
        while not self._stop.is_set():
            try:
                conn, _ = self._sock.accept()
            except socket.timeout:
                continue
            except OSError:
                if self._stop.is_set():
                    break
                continue
            t = threading.Thread(target=self._serve_conn, args=(conn,), daemon=True)
            t.start()
            self._threads.append(t)
        self._cleanup()

    def stop(self) -> None:
        self._stop.set()

    def _handle_signal(self, signum, frame) -> None:
        self.stop()

    def _cleanup(self) -> None:
        if self._sock:
            try:
                self._sock.close()
            except OSError:
                pass
        if self.socket_path.exists():
            try:
                self.socket_path.unlink()
            except OSError:
                pass

    # -- per connection ----------------------------------------------------
    def _serve_conn(self, conn: socket.socket) -> None:
        try:
            while not self._stop.is_set():
                try:
                    msg = _read_message(conn)
                except (ConnectionError, json.JSONDecodeError):
                    break
                req_id = msg.get("id")
                method = msg.get("method", "")
                params = msg.get("params") or {}
                if "method" not in msg:
                    _write_message(conn, {"jsonrpc": "2.0", "id": req_id, "error": {
                        "code": -32600, "message": "invalid request"}})
                    continue
                handler = self.methods.get(method)
                if handler is None:
                    _write_message(conn, {"jsonrpc": "2.0", "id": req_id, "error": {
                        "code": -32601, "message": f"unknown method: {method}"}})
                    continue
                try:
                    result = handler(params) if params is not None else handler({})
                    _write_message(conn, {"jsonrpc": "2.0", "id": req_id, "result": result})
                except IpcError as e:
                    _write_message(conn, {"jsonrpc": "2.0", "id": req_id, "error": {
                        "code": e.jsonrpc_code, "message": e.message,
                        "data": {"code": e.code, "retriable": e.retriable, "details": e.details}}})
                except AetherError as e:
                    _write_message(conn, {"jsonrpc": "2.0", "id": req_id, "error": {
                        "code": -32000, "message": e.message, "data": e.to_dict()}})
                except Exception as e:  # noqa: BLE001 — surfaced truthfully to caller
                    _write_message(conn, {"jsonrpc": "2.0", "id": req_id, "error": {
                        "code": -32603, "message": f"internal error: {e}"}})
        finally:
            try:
                conn.close()
            except OSError:
                pass

    def peer_credentials(self, conn: socket.socket) -> dict:
        """SO_PEERCRED — uid/gid/pid of the connecting process (Linux)."""
        creds = conn.getsockopt(socket.SOL_SOCKET, socket.SO_PEERCRED,
                                struct.calcsize("3i"))
        pid, uid, gid = struct.unpack("3i", creds)
        return {"pid": pid, "uid": uid, "gid": gid}


def call(socket_path: Path | str, method: str, params: dict | None = None,
         *, timeout: float = 10.0) -> dict:
    """Send one JSON-RPC request; return the result. Raises IpcError on error."""
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    sock.settimeout(timeout)
    try:
        sock.connect(str(socket_path))
        _write_message(sock, {"jsonrpc": "2.0", "id": 1, "method": method,
                              "params": params or {}})
        reply = _read_message(sock)
    except socket.timeout as e:
        raise IpcError("E_TIMEOUT", f"{method}: timed out after {timeout}s", jsonrpc_code=-32001) from e
    except (ConnectionError, FileNotFoundError, socket.error) as e:
        raise IpcError("E_UNREACHABLE", f"{method}: service unreachable at {socket_path}: {e}",
                       jsonrpc_code=-32002, retriable=True) from e
    finally:
        try:
            sock.close()
        except OSError:
            pass
    if "error" in reply:
        err = reply["error"]
        data = err.get("data") or {}
        raise IpcError(data.get("code", "E_REMOTE"), err.get("message", "remote error"),
                       jsonrpc_code=err.get("code", -32000),
                       retriable=data.get("retriable", False), details=data.get("details"))
    return reply.get("result", {})
