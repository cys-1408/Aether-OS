"""aether-update CLI: check | stage | install | rollback."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from update_checker import check  # noqa: E402
from staging import stage  # noqa: E402
from apply import apply  # noqa: E402
from rollback import rollback  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser(prog="aether-update")
    ap.add_argument("action", choices=["check", "stage", "install", "rollback"])
    args = ap.parse_args()
    if args.action == "check":
        print(json.dumps(check(), indent=2))
    elif args.action == "stage":
        print(json.dumps(stage()))
    elif args.action == "install":
        print(json.dumps({"confirmed": True, "result": apply(confirmed=True)}))
    elif args.action == "rollback":
        print(json.dumps(rollback()))
    return 0


if __name__ == "__main__":
    sys.exit(main())
