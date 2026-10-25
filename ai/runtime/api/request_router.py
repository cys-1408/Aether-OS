"""Task-class routing: interactive vs extraction vs background queues."""
from __future__ import annotations

QUEUE_FOR = {
    "assistant": "interactive", "code": "interactive", "summarize": "interactive",
    "concept": "extraction", "embeddings": "background", "extraction": "background",
}


def queue_for(task_class: str) -> str:
    return QUEUE_FOR.get(task_class, "background")
