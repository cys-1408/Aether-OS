"""Inotify (ctypes) watcher with polling reconciler fallback."""
from __future__ import annotations

import ctypes
import ctypes.util
import struct
import threading
from pathlib import Path

EVENTS = {"IN_CLOSE_WRITE": 0x00000008, "IN_MOVED_TO": 0x00000080,
          "IN_MOVED_FROM": 0x00000040, "IN_CREATE": 0x00000100,
          "IN_DELETE": 0x00000200, "IN_MODIFY": 0x00000002}
MASK = 0x00000200 | 0x00000040 | 0x00000080 | 0x00000008 | 0x00000100  # del|moved|create|close_write


class Watcher:
    def __init__(self, config: dict, scheduler):
        self.config = config
        self.scheduler = scheduler
        self._stop = threading.Event()
        self._libc = None
        try:
            self._libc = ctypes.CDLL(ctypes.util.find_library("c") or "libc.so.6", use_errno=True)
        except OSError:
            self._libc = None

    def start(self) -> None:
        threading.Thread(target=self._loop, daemon=True).start()

    def stop(self) -> None:
        self._stop.set()

    def _expand_roots(self) -> list[Path]:
        roots = []
        for r in self.config.get("watch_roots", []):
            p = Path(str(r).replace("~", str(Path.home()))).expanduser()
            if p.exists():
                roots.append(p)
        return roots

    def _loop(self) -> None:
        if not self._libc:
            self._poll_loop()
            return
        fd = self._libc.inotify_init1(0o4000)  # IN_NONBLOCK
        if fd < 0:
            self._poll_loop()
            return
        wd_map = {}
        for root in self._expand_roots():
            self._add_watch_recursive(fd, root, wd_map)
        buf = ctypes.create_string_buffer(4096)
        while not self._stop.is_set():
            n = self._libc.read(fd, buf, 4096)
            if n <= 0:
                self._stop.wait(1.0)
                continue
            data = buf.raw[:n]
            off = 0
            while off + 16 <= len(data):
                wd, mask, cookie, name_len = struct.unpack_from("iIII", data, off)
                name = data[off + 16:off + 16 + name_len].split(b"\x00")[0].decode(errors="replace")
                off += 16 + name_len
                base = wd_map.get(wd)
                if not base or mask & 0x00000200:  # delete
                    if base:
                        self.scheduler.on_deleted(str(base / name))
                    continue
                path = base / name
                if path.is_dir():
                    self._add_watch_recursive(fd, path, wd_map)
                    continue
                if mask & (EVENTS["IN_CLOSE_WRITE"] | EVENTS["IN_MOVED_TO"] | EVENTS["IN_CREATE"]):
                    self.scheduler.on_changed(str(path))
                elif mask & EVENTS["IN_MOVED_FROM"]:
                    self.scheduler.on_deleted(str(path))
        for wd in wd_map:
            self._libc.inotify_rm_watch(fd, wd)

    def _add_watch_recursive(self, fd, root: Path, wd_map: dict, depth: int = 0) -> None:
        if depth > 4:
            return
        from folder_exclusions import excluded
        if excluded(str(root), self.config):
            return
        wd = self._libc.inotify_add_watch(fd, str(root).encode(), MASK)
        if wd >= 0:
            wd_map[wd] = root
        try:
            for child in root.iterdir():
                if child.is_dir():
                    self._add_watch_recursive(fd, child, wd_map, depth + 1)
        except (PermissionError, OSError):
            pass

    def _poll_loop(self) -> None:
        """Fallback reconciler when inotify is unavailable."""
        import time
        seen: dict[str, float] = {}
        while not self._stop.is_set():
            for root in self._expand_roots():
                for p in root.rglob("*"):
                    if p.is_file():
                        try:
                            m = p.stat().st_mtime
                        except OSError:
                            continue
                        if seen.get(str(p)) != m:
                            seen[str(p)] = m
                            self.scheduler.on_changed(str(p))
            self._stop.wait(float(self.config.get("poll_interval_s", 30)))
