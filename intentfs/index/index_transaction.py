"""Transaction wrapper around MetadataStore.upsert."""
from __future__ import annotations


class IndexTransaction:
    def __init__(self, store):
        self.store = store
        self.records: list[dict] = []

    def add(self, record: dict) -> "IndexTransaction":
        self.records.append(record)
        return self

    def commit(self) -> int:
        n = 0
        for rec in self.records:
            self.store.upsert(rec)
            n += 1
        return n
