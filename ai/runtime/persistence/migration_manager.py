"""Forward-only migrations for runtime databases."""
from __future__ import annotations


def apply_migrations(conn, migrations: list[tuple[int, str]]) -> int:
    conn.execute("CREATE TABLE IF NOT EXISTS schema_version (v INTEGER)")
    row = conn.execute("SELECT v FROM schema_version").fetchone()
    current = row[0] if row else 0
    for version, sql in migrations:
        if version > current:
            conn.executescript(sql)
            conn.execute("UPDATE schema_version SET v=?", (version,)) if row else \
                conn.execute("INSERT INTO schema_version VALUES (?)", (version,))
            current = version
    conn.commit()
    return current
