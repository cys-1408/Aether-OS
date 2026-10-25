/*
 * test_telemetry.c - metrics parsing + redaction tests.
 */
#include "aether_telemetry/metrics.h"

#include <stdio.h>
#include <string.h>

static int checks = 0;
#define CHECK(cond)                                                         \
    do {                                                                    \
        if (!(cond)) {                                                      \
            fprintf(stderr, "FAIL %s:%d: %s\n", __FILE__, __LINE__, #cond); \
            return 1;                                                       \
        }                                                                   \
        checks++;                                                           \
    } while (0)

extern size_t aether_metrics_redact_kv(const char *text, size_t len, char *dst, size_t dst_size);

int main(void)
{
    aether_cpu_sample_t cpu1, cpu2;
    aether_mem_sample_t mem;

    CHECK(aether_metrics_read_cpu(&cpu1) == true && cpu1.ok == true);
    CHECK(aether_metrics_read_mem(&mem) == true && mem.ok == true);
    CHECK(mem.total_kb > 0);
    CHECK(aether_metrics_read_cpu(&cpu2) == true);
    double busy = aether_metrics_cpu_busy_fraction(&cpu1, &cpu2);
    CHECK(busy >= -1.0 && busy <= 1.0);
    CHECK(aether_metrics_mem_used_fraction(&mem) >= 0.0);

    char out[256];
    size_t len;

    const char *case1 = "login user password=hunter2 token=abc123 OK";
    len = aether_metrics_redact_kv(case1, strlen(case1), out, sizeof(out));
    CHECK(strstr(out, "hunter2") == NULL);
    CHECK(strstr(out, "abc123") == NULL);
    CHECK(strstr(out, "password=<redacted>") != NULL);
    CHECK(strstr(out, "token=<redacted>") != NULL);
    CHECK(strstr(out, "login user") != NULL);
    CHECK(strstr(out, "OK") != NULL);
    CHECK(len == strlen(out));

    const char *case2 = "api_key=XYZ, retries=3";
    len = aether_metrics_redact_kv(case2, strlen(case2), out, sizeof(out));
    CHECK(strstr(out, "XYZ") == NULL);
    CHECK(strstr(out, "retries=3") != NULL);

    const char *case3 = "clean text";
    len = aether_metrics_redact_kv(case3, strlen(case3), out, sizeof(out));
    CHECK(len == 10 && strcmp(out, "clean text") == 0);

    const char *case4 = "password=verylongvalue";
    len = aether_metrics_redact_kv(case4, strlen(case4), out, 8); /* tiny dst */
    CHECK(len < 8);

    printf("libaether-telemetry: %d checks passed\n", checks);
    return 0;
}
