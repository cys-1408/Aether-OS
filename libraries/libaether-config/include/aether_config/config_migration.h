/*
 * config_migration.h - versioned migration for Aether config stores.
 *
 * A store carries "version=<n>". Each migration upgrades exactly one step.
 * aether_config_migrate() applies pending migrations in order and persists
 * the bumped version atomically.
 */
#ifndef AETHER_CONFIG_CONFIG_MIGRATION_H
#define AETHER_CONFIG_CONFIG_MIGRATION_H

#include "aether_config/config_store.h"

#include <stdbool.h>

#define AETHER_CONFIG_CURRENT_VERSION 3

typedef bool (*aether_migration_fn)(aether_config_store_t *store);

typedef struct aether_migration {
    int from_version;              /* store version this step upgrades */
    const char *description;
    aether_migration_fn apply;
} aether_migration_t;

/* Registered migration table (from_version == 1..N-1). */
extern const aether_migration_t AETHER_CONFIG_MIGRATIONS[];
extern const size_t AETHER_CONFIG_MIGRATIONS_COUNT;

/* Read "version" (default 1 when absent); returns false on parse errors. */
bool aether_config_read_version(const aether_config_store_t *store, int *out_version);

/* Apply all pending migrations and save with the bumped version.
 * Returns false when a migration fails; the file is left untouched. */
bool aether_config_migrate(aether_config_store_t *store, const char *path);

#endif /* AETHER_CONFIG_CONFIG_MIGRATION_H */
