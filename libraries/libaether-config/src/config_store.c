#include "aether_config/config_store.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <errno.h>

#define LINE_MAX_LEN 512

static aether_result_t read_all(const char *path, char *buf, size_t buf_max) {
    FILE *f = fopen(path, "r");
    if (!f) return aether_err(AE_NOT_FOUND, strerror(errno));
    size_t n = fread(buf, 1, buf_max - 1, f);
    buf[n] = '\0';
    fclose(f);
    return aether_ok();
}

aether_result_t aether_config_read(const char *path, const char *key, char *out, size_t out_max) {
    static char buf[64 * 1024];
    aether_result_t r = read_all(path, buf, sizeof(buf));
    if (!r.ok) return r;
    size_t klen = strlen(key);
    char *line = buf;
    while (line && *line) {
        char *nl = strchr(line, '\n');
        if (strncmp(line, key, klen) == 0 && line[klen] == '=') {
            const char *v = line + klen + 1;
            size_t vlen = (nl ? (size_t)(nl - v) : strlen(v));
            if (vlen >= out_max) return aether_err(AE_INVALID, "value too long");
            memcpy(out, v, vlen); out[vlen] = '\0';
            return aether_ok();
        }
        line = nl ? nl + 1 : NULL;
    }
    return aether_err(AE_NOT_FOUND, "key not found");
}

aether_result_t aether_config_write(const char *path, const char *key, const char *value) {
    static char buf[64 * 1024];
    aether_result_t r = read_all(path, buf, sizeof(buf));
    int found = r.ok;
    char tmp_path[600];
    snprintf(tmp_path, sizeof(tmp_path), "%s.tmp", path);
    FILE *f = fopen(tmp_path, "w");
    if (!f) return aether_err(AE_IO, strerror(errno));
    if (found) {
        char *line = buf;
        while (line && *line) {
            char *nl = strchr(line, '\n');
            size_t llen = nl ? (size_t)(nl - line) : strlen(line);
            if ((size_t)llen > strlen(key) && strncmp(line, key, strlen(key)) == 0 && line[strlen(key)] == '=') {
                fprintf(f, "%s=%s\n", key, value);
            } else {
                fwrite(line, 1, llen, f);
                fputc('\n', f);
            }
            line = nl ? nl + 1 : NULL;
        }
    } else {
        fprintf(f, "%s=%s\n", key, value);
    }
    fclose(f);
    if (rename(tmp_path, path) < 0) return aether_err(AE_IO, strerror(errno));
    return aether_ok();
}

aether_result_t aether_config_get_version(const char *path, unsigned *version) {
    char v[32];
    aether_result_t r = aether_config_read(path, "config_version", v, sizeof(v));
    if (!r.ok) { *version = 1; return aether_ok(); }
    *version = (unsigned)atoi(v);
    return aether_ok();
}
