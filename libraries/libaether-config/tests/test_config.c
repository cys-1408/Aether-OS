/*
 * test_config.c - store + migration round-trip tests (temp dir backed).
 */
#include "aether_config/config_store.h"
#include "aether_config/config_migration.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

static int checks = 0;
#define CHECK(cond)                                                         \
    do {                                                                    \
        if (!(cond)) {                                                      \
            fprintf(stderr, "FAIL %s:%d: %s\n", __FILE__, __LINE__, #cond); \
            return 1;                                                       \
        }                                                                   \
        checks++;                                                           \
    } while (0)

int main(void)
{
    char path[] = "/tmp/aether-config-test-XXXXXX";
    int fd = mkstemp(path);
    CHECK(fd >= 0);
    close(fd);

    aether_config_store_t store;
    CHECK(aether_config_load(&store, path, true) == true);
    CHECK(store.count == 0);
    CHECK(aether_config_set(&store, "version", "1") == true);
    CHECK(aether_config_set(&store, "telemetry_opt_in", "false") == true);
    CHECK(strcmp(aether_config_get_or(&store, "telemetry_opt_in", "?"), "false") == 0);
    CHECK(aether_config_get(&store, "missing") == NULL);
    CHECK(aether_config_save(&store, path) == true);

    /* Reload from disk. */
    aether_config_store_t reloaded;
    CHECK(aether_config_load(&reloaded, path, false) == true);
    CHECK(strcmp(aether_config_get_or(&reloaded, "version", "?"), "1") == 0);

    /* Migrate 1 -> 3. */
    CHECK(aether_config_migrate(&reloaded, path) == true);
    int version = 0;
    CHECK(aether_config_read_version(&reloaded, &version) == true);
    CHECK(version == AETHER_CONFIG_CURRENT_VERSION);
    CHECK(strcmp(aether_config_get_or(&reloaded, "telemetry_consent", "?"), "false") == 0);
    CHECK(aether_config_get(&reloaded, "telemetry_opt_in") == NULL);
    CHECK(strcmp(aether_config_get_or(&reloaded, "update_auto_install", "?"), "false") == 0);

    /* Migration of an already-current store is a no-op that still saves. */
    CHECK(aether_config_migrate(&reloaded, path) == true);

    /* Removal works. */
    CHECK(aether_config_remove(&reloaded, "telemetry_consent") == true);
    CHECK(aether_config_get(&reloaded, "telemetry_consent") == NULL);

    /* Malformed lines are rejected on load. */
    FILE *fh = fopen(path, "w");
    CHECK(fh != NULL);
    fputs("this-line-has-no-equals-sign\n", fh);
    fclose(fh);
    CHECK(aether_config_load(&reloaded, path, false) == false);

    unlink(path);
    printf("libaether-config: %d checks passed\n", checks);
    return 0;
}
