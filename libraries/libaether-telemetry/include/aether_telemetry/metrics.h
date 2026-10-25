/* Local-only system metrics (never leaves the device). */
#ifndef AETHER_TELEMETRY_METRICS_H
#define AETHER_TELEMETRY_METRICS_H
typedef struct {
    unsigned long cpu_total_jiffies;
    unsigned long cpu_idle_jiffies;
    unsigned long mem_total_kb;
    unsigned long mem_available_kb;
} aether_metrics_t;
int aether_metrics_collect(aether_metrics_t *out);
int aether_metrics_redact_line(const char *in, char *out, unsigned out_max);
#endif
