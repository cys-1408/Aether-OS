"""Shared screen infrastructure: guarded GTK import + CLI input helpers."""

from __future__ import annotations

import sys

try:
    import gi
    gi.require_version("Gtk", "3.0")
    from gi.repository import Gtk  # noqa: F401
    GTK_AVAILABLE = True
except Exception:  # PyGObject absent or display-less: CLI mode still works
    GTK_AVAILABLE = False


class CliInputError(Exception):
    pass


class ScreenBase:
    """Base class for installer screens.

    Subclasses implement ``title``, ``subtitle``, ``build()`` (GTK widgets
    wired to the controller) and ``run_cli()`` (collects the same answers via
    stdin and calls controller.apply). Validation lives in the controller.
    """

    title = "Screen"
    subtitle = ""

    def __init__(self, controller):
        self.controller = controller

    # GTK API ------------------------------------------------------------
    def build(self):
        if not GTK_AVAILABLE:
            raise RuntimeError(
                "GTK3 unavailable; run the installer with --cli for the TUI fallback"
            )
        return self._build_gtk()

    def _build_gtk(self):  # pragma: no cover - requires a display
        raise RuntimeError(f"screen {type(self).__name__} does not build GTK widgets")

    def gtk_box(self, spacing=12, vertical=True):
        from gi.repository import Gtk

        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL if vertical
                      else Gtk.Orientation.HORIZONTAL, spacing=spacing)
        box.set_margin_top(24)
        box.set_margin_bottom(24)
        box.set_margin_start(32)
        box.set_margin_end(32)
        return box

    def gtk_heading(self):
        from gi.repository import Gtk

        box = self.gtk_box(spacing=6)
        title = Gtk.Label(xalign=0.0)
        title.set_markup(f"<span size='x-large' weight='bold'>{self.title}</span>")
        subtitle = Gtk.Label(xalign=0.0)
        subtitle.set_markup(f"<span alpha='65%'>{self.subtitle}</span>")
        subtitle.set_line_wrap(True)
        box.pack_start(title, False, False, 0)
        if self.subtitle:
            box.pack_start(subtitle, False, False, 0)
        return box

    # CLI API ------------------------------------------------------------
    def run_cli(self) -> None:  # pragma: no cover - interactive
        raise RuntimeError(f"screen {type(self).__name__} has no CLI mode")

    @staticmethod
    def cli_print(text: str = "") -> None:
        print(text, flush=True)

    @classmethod
    def cli_header(cls) -> None:
        print(f"\n=== {cls.title} ===", flush=True)
        if cls.subtitle:
            print(cls.subtitle, flush=True)

    @staticmethod
    def cli_ask(prompt: str, *, validator=None, default: str | None = None) -> str:
        while True:
            suffix = f" [{default}]" if default else ""
            try:
                raw = input(f"{prompt}{suffix}: ").strip()
            except EOFError as exc:
                raise CliInputError("input stream closed") from exc
            if not raw and default is not None:
                raw = default
            if validator is None:
                return raw
            problem = validator(raw)
            if problem is None:
                return raw
            print(f"  invalid: {problem}", flush=True)

    @staticmethod
    def cli_confirm(prompt: str, default: bool = False) -> bool:
        hint = "Y/n" if default else "y/N"
        raw = input(f"{prompt} [{hint}]: ").strip().lower()
        if not raw:
            return default
        return raw in ("y", "yes")

    @staticmethod
    def cli_choose(prompt: str, options: list[str], default: str | None = None) -> str:
        for i, option in enumerate(options, start=1):
            print(f"  {i}) {option}", flush=True)
        while True:
            raw = input(f"{prompt} (1-{len(options)}): ").strip()
            if not raw and default:
                return default
            if raw.isdigit() and 1 <= int(raw) <= len(options):
                return options[int(raw) - 1]
            print("  invalid choice", flush=True)

    @staticmethod
    def cli_secret(prompt: str) -> str:
        import getpass

        return getpass.getpass(f"{prompt}: ")
