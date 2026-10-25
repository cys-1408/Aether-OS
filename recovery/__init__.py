"""AetherOS recovery environment (aether-recovery.target entry point)."""

__version__ = "1.0.0"

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent
_LIBAETHER = REPO_ROOT / "libraries" / "libaether-core" / "python"
if _LIBAETHER.is_dir() and str(_LIBAETHER) not in sys.path:
    sys.path.insert(0, str(_LIBAETHER))
