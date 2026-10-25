#include "aether_core/resource_limits.h"

/* Budget defaults shared with the Python services (aether_core.ResourceBudget). */
aether_budget_t aether_budget_default(void) {
    aether_budget_t b = { .max_mem_mb = 512, .cpu_percent = 50, .max_concurrent = 2, .disk_mb = 2048 };
    return b;
}
