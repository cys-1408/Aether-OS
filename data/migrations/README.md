# Data schema migrations

Aether persists versioned records in four owned stores; every store carries a
`schemaVersion` (or a numbered SQL migration table) and all migrations are
applied **forward-only**.

## Stores and ordering

| Store | Location | Migration mechanism |
| --- | --- | --- |
| IntentFS metadata | `$XDG_DATA_HOME/aether/intentfs/intentfs.db` | numbered SQL files in `intentfs/index/migrations/`, applied in lexicographic order (e.g. `001_initial_schema.sql`) |
| Action ledger | `$XDG_DATA_HOME/aether/ledger/ledger.db` | `miso/ledger/schema.sql` + version tag row (`PRAGMA user_version`) |
| Workspaces | `$XDG_DATA_HOME/aether/workspaces/` | `miso/workspaces/workspace_migrations/001_initial.py` Python migrations |
| Package state | `/var/lib/aether/pm/transactions.db` | `package-manager/core/package_database.py` version check |

## Rules

1. Associates files are never renumbered after release; add `002_*`, never edit
   applied migrations.
2. Migration failure keeps the old store intact (all migrations run inside a
   transaction; workspaces migrate into a `.new` file first and swap atomically).
3. Rollback of migrations is **not supported**; downgrade of the OS leaves the
   newer-format store untouched and the older reader reports an honest
   `unsupported schema version` error.
4. Recovery of a corrupt store is handled by the Recovery Center
   (`intentfs/index/rebuild_index.py` for IntentFS; ledger can be re-created
   from the append-only journal only via repair, never silently).
5. User settings/system settings JSON files migrate with
   `libraries/libaether-config/src/config_migration.c` (version bump + field
   moves); unknown new fields are preserved, never dropped.

## Schema files

Canonical JSON schemas live in `data/schemas/`; `protocols/schemas/` mirrors
the IPC-facing subset. `data/schemas` is authoritative — update it first and
sync the mirror in the same change.
