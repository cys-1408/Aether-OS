"""Session entry: invoked by greetd/sway config to start the shell."""
from __future__ import annotations

import os
import subprocess
import sys


def start_session() -> int:
    env = dict(os.environ)
    env.setdefault("XDG_CURRENT_DESKTOP", "Aether")
    env.setdefault("AETHER_SESSION", "1")
    # compositor must be running; if not (TTY), start sway with our config
    if not os.environ.get("SWAYSOCK"):
        print("SWAYSOCK not set — launch via sway session (see compositor/wayland_session.py)",
              file=sys.stderr)
        return 1
    return subprocess.call(["/usr/bin/aether-shell"], env=env)


if __name__ == "__main__":
    sys.exit(start_session())
