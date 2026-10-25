import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / 'libraries/libaether-core/python'))
"""Interactive lane: priority, concurrency 1."""

import threading

_sem = threading.Semaphore(1 if "interactive" in "interactive_queue" else 2)


def acquire():
    return _sem
