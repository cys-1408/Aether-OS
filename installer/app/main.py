"""aether-installer entry: GTK app or --cli TUI mode."""
from __future__ import annotations

import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "libraries/libaether-core/python"))
sys.path.insert(0, str(HERE.parent))

from installer_controller import InstallerController  # noqa: E402
from installer_state import InstallerState  # noqa: E402


def require_root() -> None:
    if os.geteuid() != 0 and "--dry-run" not in sys.argv:
        print("The installer must run as root from the live ISO (or use --dry-run).", file=sys.stderr)
        sys.exit(77)


def run_cli(dry_run: bool) -> int:
    from screens.target_disk_screen import pick_disk_cli
    from screens.user_account_screen import ask_user_cli
    from screens.encryption_screen import ask_encryption_cli
    from storage.destructive_action_guard import typed_confirmation
    require_root()
    state = InstallerState()
    controller = InstallerController(state, dry_run=dry_run)
    disk = pick_disk_cli()
    enc = ask_encryption_cli()
    user = ask_user_cli()
    typed = "" if dry_run else input(f"Type the disk name to confirm ERASE of {disk}: ").strip()
    plan = {"target_disk": disk, "encryption": enc, "user": user, "confirm_typed": typed,
            "choices": {"mode": "cli"}}
    result = controller.run_plan(plan)
    print("Install complete." if result.get("ok") else "Install FAILED — see installer log.")
    return 0 if result.get("ok") else 1


def run_gtk() -> int:
    try:
        import gi
        gi.require_version("Gtk", "3.0")
        from gi.repository import Gtk
    except (ImportError, ValueError):
        return run_cli("--dry-run" in sys.argv)

    from screens.welcome_screen import WelcomeScreen
    win = WelcomeScreen()
    win.show_all()
    Gtk.main()
    return 0


if __name__ == "__main__":
    if "--cli" in sys.argv or not (os.environ.get("DISPLAY") or os.environ.get("WAYLAND_DISPLAY")):
        sys.exit(run_cli("--dry-run" in sys.argv))
    sys.exit(run_gtk())
