#include "aether_config/config_store.h"
#include <stdio.h>

/* Forward-only migration: bump config_version and apply per-step transforms.
 * Returns the resulting version. */
aether_result_t aether_config_migrate(const char *path, unsigned target_version, unsigned *applied) {
    unsigned current = 0;
    aether_result_t r = aether_config_get_version(path, &current);
    if (!r.ok) return r;
    *applied = current;
    char buf[32];
    while (current < target_version) {
        /* Per-version transforms would be dispatched here; v1 has none. */
        current++;
        snprintf(buf, sizeof(buf), "%u", current);
        r = aether_config_write(path, "config_version", buf);
        if (!r.ok) return r;
    }
    *applied = current;
    return aether_ok();
}
