"""Miso — the AetherOS agent stack.

Contains the Miso user agent, the CapabilityOS (catalogs + registry), the
system broker, the policy engine, real capability implementations, the Action
Ledger service, Living Workspaces service, presence, safety primitives and the
assistant UI.
"""

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
_CORE = REPO_ROOT / "libraries" / "libaether-core" / "python"
for _path in (str(_CORE), str(REPO_ROOT)):
    if _path not in sys.path:
        sys.path.insert(0, _path)

VERSION = "1.0.0"
