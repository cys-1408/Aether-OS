import sys
from pathlib import Path
_p = Path(__file__).resolve()
sys.path.insert(0, str(_p.parents[2] / 'libraries/libaether-core/python'))
"""Recovery TUI entry point (runs on aether-recovery.target)."""
from recovery_session import RecoverySession


def main() -> int:
    session = RecoverySession()
    return session.run()


if __name__ == "__main__":
    sys.exit(main())
