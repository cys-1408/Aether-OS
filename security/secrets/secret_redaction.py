import sys
from pathlib import Path
_p = Path(__file__).resolve()
sys.path.insert(0, str(_p.parents[2] / 'libraries/libaether-core/python'))
"""Secret redaction (delegates to the shared patterns)."""
from aether_core.logging_setup import redact_text  # noqa: F401


def redact(text: str) -> str:
    return redact_text(text)
