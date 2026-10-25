"""Subscribe to health/notification events for opt-in presence."""
from __future__ import annotations

import threading


class EventSubscriber:
    def __init__(self, rules):
        self.rules = rules

    def start(self) -> None:
        def loop():
            import time
            from aether_core.ipc import call
            from aether_core import paths
            seen = set()
            while True:
                try:
                    data = call(paths.system_socket("health"), "Health.events", {}, timeout=10)
                    for ev in (data or {}).get("events", []):
                        key = ev.get("id")
                        if key and key not in seen and self.rules.allows(ev):
                            seen.add(key)
                            self._notify(ev)
                except Exception:
                    pass
                time.sleep(20)
        threading.Thread(target=loop, daemon=True).start()

    def _notify(self, ev: dict) -> None:
        from aether_core.ipc import call
        from aether_core import paths
        try:
            call(paths.system_socket("notifications"), "Notify.notify",
                 {"source": "miso-presence", "category": ev.get("category", "system"),
                  "title": ev.get("title", "Miso noticed something"),
                  "body": observed_only(ev)}, timeout=5)
        except Exception:
            pass


def observed_only(ev: dict) -> str:
    """Presence messages state OBSERVED facts; interpretations are labeled."""
    return f"observed: {ev.get('summary', ev.get('title', 'event'))} (facts only)"
