"""Mines game state: REAL minesweeper logic (first-click safe, flood reveal)."""
from __future__ import annotations

import random
import time


class MinesGame:
    def __init__(self, cols: int, rows: int, mines: int):
        self.cols, self.rows, self.mine_count = cols, rows, mines
        self.reset()

    def reset(self) -> None:
        n = self.cols * self.rows
        self.mines = [False] * n
        self.revealed = [False] * n
        self.flagged = [False] * n
        self.counts = [0] * n
        self.started = False
        self.over = False
        self.won = False
        self._t0 = 0.0

    def neighbors(self, i: int) -> list[int]:
        x, y = i % self.cols, i // self.cols
        out = []
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if 0 <= nx < self.cols and 0 <= ny < self.rows:
                    out.append(ny * self.cols + nx)
        return out

    def _place(self, avoid: int) -> None:
        banned = {avoid} | set(self.neighbors(avoid))
        placed = 0
        while placed < self.mine_count:
            i = random.randrange(self.cols * self.rows)
            if i in banned or self.mines[i]:
                continue
            self.mines[i] = True
            placed += 1
        for i in range(self.cols * self.rows):
            if not self.mines[i]:
                self.counts[i] = sum(1 for j in self.neighbors(i) if self.mines[j])

    def reveal(self, i: int) -> list[dict]:
        events = []
        if self.over or self.flagged[i] or self.revealed[i]:
            return events
        if not self.started:
            self.started = True
            self._t0 = time.monotonic()
            self._place(i)
        if self.mines[i]:
            self.revealed[i] = True
            self.over = True
            events.append({"type": "boom", "cell": i})
            return events
        stack = [i]
        while stack:
            k = stack.pop()
            if self.revealed[k] or self.flagged[k]:
                continue
            self.revealed[k] = True
            if self.counts[k] == 0:
                stack.extend(self.neighbors(k))
        if sum(self.revealed) == self.cols * self.rows - self.mine_count:
            self.over = True
            self.won = True
            events.append({"type": "win"})
        return events

    def toggle_flag(self, i: int) -> None:
        if not self.over and not self.revealed[i]:
            self.flagged[i] = not self.flagged[i]

    def cell_state(self, i: int) -> tuple[str, int]:
        if self.revealed[i]:
            return ("mine" if self.mines[i] else "number"), self.counts[i]
        return ("flag" if self.flagged[i] else "hidden"), 0

    def elapsed(self) -> int:
        return int(time.monotonic() - self._t0) if self.started else 0
