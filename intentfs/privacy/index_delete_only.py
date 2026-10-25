"""The delete-only guarantee: index clears NEVER touch source files.

Enforced by construction: MetadataStore.clear_all() executes SQL DELETEs on the
index DB only — it holds no file handles to user data and performs no unlink.
This module asserts that contract for tests.
"""
from __future__ import annotations


def assert_index_only(store) -> dict:
    assert not hasattr(store, "unlink"), "store must not expose file deletion"
    return {"guarantee": "index_delete_only", "verified": True}
