"""REAL process table from /proc (pid, name, cpu%%, rss, uid, state)."""
from __future__ import annotations

import os
import signal
import subprocess
import time

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk


class ProcessTable:
    def __init__(self):
        self.model = Gtk.ListStore(int, str, float, int, str, str)  # pid, name, cpu, rss_kb, uid, state
        self.tree = Gtk.TreeView(model=self.model)
        for i, title in enumerate(("PID", "Name", "CPU %", "RSS KB", "UID", "State")):
            cell = Gtk.CellRendererText()
            col = Gtk.TreeViewColumn(title, cell, text=i)
            col.set_sort_column_id(i)
            self.tree.append_column(col)
        self.tree.get_selection().set_mode(Gtk.SelectionMode.SINGLE)
        self._last = {}
        self.refresh()

    def refresh(self) -> None:
        now = time.monotonic()
        rows = []
        for pid in os.listdir("/proc"):
            if not pid.isdigit():
                continue
            try:
                with open(f"/proc/{pid}/stat") as fh:
                    parts = fh.read().rsplit(")", 1)
                name = parts[0].split("(", 1)[1]
                fields = parts[1].split()
                utime, stime = int(fields[11]), int(fields[12])
                state = fields[0]
            except (OSError, IndexError, ValueError):
                continue
            try:
                with open(f"/proc/{pid}/statm") as fh:
                    rss_kb = int(fh.read().split()[1]) * 4
            except (OSError, IndexError, ValueError):
                rss_kb = 0
            try:
                uid = os.stat(f"/proc/{pid}").st_uid
            except OSError:
                uid = -1
            jiffies = utime + stime
            prev = self._last.get(int(pid), (0, None))
            cpu = 0.0
            if prev[1] is not None and now > prev[1]:
                cpu = (jiffies - prev[0]) / ((now - prev[1]) * os.sysconf("SC_CLK_TCK")) * 100
            self._last[int(pid)] = (jiffies, now)
            rows.append((int(pid), name, round(cpu, 1), rss_kb, uid, state))
        rows.sort(key=lambda r: r[2], reverse=True)
        self.model.clear()
        for r in rows[:120]:
            self.model.append(list(r))

    def selected(self) -> tuple[int, str] | tuple[None, None]:
        model, iter_ = self.tree.get_selection().get_selected()
        if not iter_:
            return None, None
        return model[iter_][0], model[iter_][1]

    def kill(self, pid: int) -> None:
        try:
            os.kill(pid, signal.SIGTERM)
        except OSError as e:
            try:
                out = subprocess.run(["pkexec", "kill", str(pid)], capture_output=True, timeout=10)
                if out.returncode != 0:
                    raise OSError(f"pkexec kill failed: {out.stderr.decode()[:120]}")
            except (FileNotFoundError, subprocess.TimeoutExpired) as e2:
                raise OSError(f"cannot kill {pid}: {e}; {e2}")
