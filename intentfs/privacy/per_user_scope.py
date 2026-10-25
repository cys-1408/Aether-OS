"""Per-user scope: users only ever see their own index."""
from __future__ import annotations


def db_path_for(uid: int) -> Path:
    import pwd
    from pathlib import Path
    home = Path(pwd.getpwuid(uid).pw_dir)
    return home / ".local/share/aether/intentfs/intentfs.db"
