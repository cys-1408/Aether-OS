import sys
from pathlib import Path
_p = Path(__file__).resolve()
sys.path.insert(0, str(_p.parents[2] / 'libraries/libaether-core/python'))
"""Secret store: kernel keyring via keyctl, 0600-file fallback."""
import subprocess
from pathlib import Path


def store(name: str, secret: str) -> dict:
    try:
        out = subprocess.run(["keyctl", "add", "user", f"aether:{name}", secret, "@u"],
                             capture_output=True, text=True, timeout=10)
        if out.returncode == 0:
            return {"stored": "keyring", "id": out.stdout.strip()}
    except FileNotFoundError:
        pass
    fallback = Path.home() / ".config/aether/secrets"
    fallback.mkdir(parents=True, exist_ok=True, mode=0o700)
    target = fallback / name
    target.write_text(secret)
    target.chmod(0o600)
    return {"stored": "file", "path": str(target)}


def load(name: str) -> str | None:
    try:
        out = subprocess.run(["keyctl", "print", f"aether:{name}"],
                             capture_output=True, text=True, timeout=10)
        if out.returncode == 0:
            return out.stdout
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass
    fallback = Path.home() / ".config/aether/secrets" / name
    return fallback.read_text() if fallback.exists() else None
