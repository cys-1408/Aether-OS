#include "aether_files/file_identity.h"
#include <sys/stat.h>
#include <stdio.h>
#include <stdint.h>

static uint64_t fnv1a(const char *s) {
    uint64_t h = 1469598103934665603ULL;
    while (*s) { h ^= (uint8_t)*s++; h *= 1099511628211ULL; }
    return h;
}

aether_result_t aether_file_identity(const char *path, char *out, size_t out_max) {
    struct stat st;
    if (stat(path, &st) < 0) return aether_err(AE_NOT_FOUND, "stat failed");
    char basis[256];
    snprintf(basis, sizeof(basis), "%ld:%ld:%ld:%ld",
             (long)st.st_dev, (long)st.st_ino, (long)st.st_size, (long)st.st_mtime);
    snprintf(out, out_max, "%016llx", (unsigned long long)fnv1a(basis));
    return aether_ok();
}
