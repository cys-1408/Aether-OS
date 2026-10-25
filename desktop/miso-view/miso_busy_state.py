"""Busy handling: animation + panel state while agent works."""
from __future__ import annotations


class BusyState:
    def __init__(self, view, panel):
        self.view = view
        self.panel = panel

    def enter(self, task: str):
        self.view.set_state("searching")
        self.panel.status_chip.set_text("BUSY")

    def exit(self, state: str = "idle"):
        self.view.set_state(state)
        self.panel.status_chip.set_text(state.upper())
