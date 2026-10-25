#include "aether_telemetry/metrics.h"
#include <stdio.h>
#include <string.h>

int aether_metrics_collect(aether_metrics_t *out) {
    FILE *f = fopen("/proc/stat", "r");
    if (!f) return -1;
    char line[256];
    unsigned long user = 0, nice = 0, sys = 0, idle = 0, iowait = 0, irq = 0, softirq = 0, steal = 0;
    while (fgets(line, sizeof(line), f)) {
        if (strncmp(line, "cpu ", 4) == 0) {
            sscanf(line + 4, "%lu %lu %lu %lu %lu %lu %lu %lu",
                   &user, &nice, &sys, &idle, &iowait, &irq, &softirq, &steal);
            break;
        }
    }
    fclose(f);
    out->cpu_total_jiffies = user + nice + sys + idle + iowait + irq + softirq + steal;
    out->cpu_idle_jiffies = idle + iowait;
    f = fopen("/proc/meminfo", "r");
    if (!f) return -1;
    out->mem_total_kb = out->mem_available_kb = 0;
    while (fgets(line, sizeof(line), f)) {
        if (strncmp(line, "MemTotal:", 9) == 0) sscanf(line + 9, "%lu", &out->mem_total_kb);
        if (strncmp(line, "MemAvailable:", 13) == 0) sscanf(line + 13, "%lu", &out->mem_available_kb);
    }
    fclose(f);
    return 0;
}
