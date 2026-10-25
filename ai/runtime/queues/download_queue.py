import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / 'libraries/libaether-core/python'))
"""Download lane: bandwidth-bounded."""

import threading

_sem = threading.Semaphore(1 if "interactive" in "download_queue" else 2)


def acquire():
    return _sem
