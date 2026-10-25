# aether_core (Python)

Shared foundation imported by every Aether service:

```python
import sys, pathlib
REPO_ROOT = pathlib.Path(__file__).resolve().parents[N]  # depth depends on caller
sys.path.insert(0, str(REPO_ROOT / "libraries/libaether-core/python"))
from aether_core.ipc import JsonRpcServer, call
```

Installed system-wide by the aether-services package to /usr/lib/aether/python/aether_core
(the installed services prepend that directory instead). API contract: CONVENTIONS.md §3.
