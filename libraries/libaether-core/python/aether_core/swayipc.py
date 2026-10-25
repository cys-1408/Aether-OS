"""Minimal i3/sway IPC client (stdlib only) — used by the desktop shell.

Protocol: b"i3-ipc" + u32 length + u32 type + payload (JSON).
"""
from __future__ import annotations

import json
import os
import socket
import struct
from typing import Callable

MAGIC = b"i3-ipc"
RUN_COMMAND, GET_WORKSPACES, SUBSCRIBE, GET_OUTPUTS = 0, 1, 2, 3
GET_TREE = 4
GET_MARKS, GET_BAR_CONFIG, GET_VERSION = 5, 6, 7


class SwayIPC:
    def __init__(self, socket_path: str | None = None):
        self.socket_path = socket_path or os.environ.get("SWAYSOCK", "")
        if not self.socket_path:
            raise ConnectionError("SWAYSOCK not set and no path given")

    def _send(self, mtype: int, payload: str = "") -> dict:
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        sock.settimeout(10.0)
        try:
            sock.connect(self.socket_path)
            data = payload.encode("utf-8")
            sock.sendall(MAGIC + struct.pack("=II", len(data), mtype) + data)
            header = b""
            while len(header) < 14:
                header += sock.recv(14 - len(header))
            magic = header[:6]
            if magic != MAGIC:
                raise ConnectionError("bad sway IPC magic")
            length, rtype = struct.unpack("=II", header[6:14])
            body = b""
            while len(body) < length:
                body += sock.recv(length - len(body))
            return json.loads(body.decode("utf-8"))
        finally:
            sock.close()

    def run_command(self, cmd: str) -> list:
        return self._send(RUN_COMMAND, cmd)

    def get_tree(self) -> dict:
        return self._send(GET_TREE)

    def get_workspaces(self) -> list:
        return self._send(GET_WORKSPACES)

    def get_outputs(self) -> list:
        return self._send(GET_OUTPUTS)

    def get_version(self) -> dict:
        return self._send(GET_VERSION)

    def subscribe(self, events: list[str], callback: Callable[[dict], None]) -> None:
        """Blocking subscription loop (run in a dedicated thread)."""
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        sock.settimeout(None)
        sock.connect(self.socket_path)
        data = json.dumps(events).encode("utf-8")
        sock.sendall(MAGIC + struct.pack("=II", len(data), SUBSCRIBE) + data)
        header = b""
        while len(header) < 14:
            header += sock.recv(14 - len(header))
        length, _ = struct.unpack("=II", header[6:14])
        body = b""
        while len(body) < length:
            body += sock.recv(length - len(body))
        ack = json.loads(body.decode("utf-8"))
        if not ack.get("success"):
            raise ConnectionError(f"sway subscribe failed: {ack}")
        while True:
            header = b""
            while len(header) < 14:
                header += sock.recv(14 - len(header))
            length, _ = struct.unpack("=II", header[6:14])
            body = b""
            while len(body) < length:
                body += sock.recv(length - len(body))
            callback(json.loads(body.decode("utf-8")))
