#include "aether_telemetry/metrics.h"
#include <string.h>

/* Scrub credential-looking substrings from any exported metric line. */
int aether_metrics_redact_line(const char *in, char *out, unsigned out_max) {
    unsigned o = 0;
    for (const char *p = in; *p && o + 1 < out_max; p++) {
        if (strncmp(p, "password", 8) == 0 || strncmp(p, "token", 5) == 0 ||
            strncmp(p, "api_key", 7) == 0) {
            const char *end = p;
            while (*end && *end != ' ') end++;
            if (o + 10 >= out_max) break;
            memcpy(out + o, "[REDACTED]", 10); o += 10;
            p = end - 1;
            continue;
        }
        out[o++] = *p;
    }
    out[o] = '\0';
    return 0;
}
