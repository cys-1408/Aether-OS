"""aetherctl — CLI to drive shell actions (used by sway keybindings)."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "libraries/libaether-core/python"))

from aether_core.ipc import call  # noqa: E402
from aether_core.errors import IpcError  # noqa: E402
from aether_core import paths  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser(prog="aetherctl")
    ap.add_argument("action", choices=["launcher", "toggle-miso", "focus", "end-focus", "toast"])
    ap.add_argument("arg", nargs="?", default="")
    args = ap.parse_args()
    sock = paths.user_socket("shell")
    try:
        if args.action == "launcher":
            call(sock, "Shell.launcher_toggle", {})
        elif args.action == "toggle-miso":
            call(sock, "Shell.toast", {"title": "Miso", "body": "assistant toggle requested"})
        elif args.action == "focus":
            call(sock, "Shell.start_focus", {"minutes": int(args.arg) if args.arg else 25})
        elif args.action == "end-focus":
            call(sock, "Shell.end_focus", {})
        elif args.action == "toast":
            call(sock, "Shell.toast", {"title": args.arg})
        return 0
    except IpcError as e:
        print(f"aetherctl: {e.message}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
