"""aether-pm CLI (install/remove/update/search/info/status/rollback)."""
from __future__ import annotations

import argparse
import json
import sys

sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parents[2] / "libraries/libaether-core/python"))
sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parents[1]))

from core.package_manager import install, remove, update_all, search, installed, info, history, rollback_last  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser(prog="aether-pm")
    ap.add_argument("action", choices=["install", "remove", "update", "search", "info", "status", "rollback", "history"])
    ap.add_argument("packages", nargs="*")
    args = ap.parse_args()
    try:
        if args.action == "install":
            print(json.dumps(install(args.packages)))
        elif args.action == "remove":
            print(json.dumps(remove(args.packages)))
        elif args.action == "update":
            print(json.dumps(update_all()))
        elif args.action == "search":
            print(json.dumps(search(args.packages[0] if args.packages else ""), indent=2))
        elif args.action == "info":
            print(json.dumps(info(args.packages[0]), indent=2))
        elif args.action == "status":
            print(json.dumps({"installed": len(installed())}))
        elif args.action == "rollback":
            print(json.dumps(rollback_last()))
        elif args.action == "history":
            print(json.dumps(history(), indent=2))
        return 0
    except Exception as e:  # noqa: BLE001
        print(f"aether-pm: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
