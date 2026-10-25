"""Launcher protocol: --open <path> + app-id activation for Shell.open_app."""
from __future__ import annotations

import argparse


def parse_launcher_args(argv: list[str]) -> dict:
    ap = argparse.ArgumentParser(allow_abbrev=False)
    ap.add_argument("--open", dest="open_path", default=None, help="file to open")
    ap.add_argument("--new", action="store_true", help="create a new document")
    args, _ = ap.parse_known_args(argv)
    return {"open_path": args.open_path, "new": args.new}
