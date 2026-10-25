/* Shared resource-budget structure (mirrors aether_core.ResourceBudget). */
#ifndef AETHER_CORE_RESOURCE_LIMITS_H
#define AETHER_CORE_RESOURCE_LIMITS_H
typedef struct {
    unsigned max_mem_mb;
    unsigned cpu_percent;
    unsigned max_concurrent;
    unsigned disk_mb;
} aether_budget_t;
#endif
