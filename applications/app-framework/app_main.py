"""run_app factory for Aether applications."""
from __future__ import annotations

import sys


def run_app(app, argv=None) -> int:
    return app.run(argv if argv is not None else sys.argv)
