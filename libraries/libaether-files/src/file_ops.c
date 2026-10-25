#include "aether_files/file_ops.h"
#include <errno.h>
#include <string.h>
#include <fcntl.h>
#include <stdio.h>
#include <unistd.h>
#include <sys/stat.h>

aether_result_t aether_file_copy_atomic(const char *src, const char *dst) {
    int in = open(src, O_RDONLY);
    if (in < 0) return aether_err(AE_NOT_FOUND, strerror(errno));
    char tmp[1024];
    snprintf(tmp, sizeof(tmp), "%s.aether-tmp", dst);
    int out = open(tmp, O_WRONLY | O_CREAT | O_TRUNC, 0644);
    if (out < 0) { close(in); return aether_err(AE_IO, strerror(errno)); }
    char buf[65536];
    ssize_t n;
    while ((n = read(in, buf, sizeof(buf))) > 0) {
        if (write(out, buf, (size_t)n) != n) { close(in); close(out); unlink(tmp); return aether_err(AE_IO, "short write"); }
    }
    fsync(out);
    close(in); close(out);
    if (rename(tmp, dst) < 0) { unlink(tmp); return aether_err(AE_IO, strerror(errno)); }
    return aether_ok();
}
