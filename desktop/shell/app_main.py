"""aether-shell entry point: starts the native desktop process."""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[2]
for p in (REPO_ROOT / "libraries/libaether-core/python", HERE.parent):
    sys.path.insert(0, str(p))

from shell_application import ShellApplication  # noqa: E402

if __name__ == "__main__":
    sys.exit(ShellApplication().run(sys.argv))
