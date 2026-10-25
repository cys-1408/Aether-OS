/*
 * test_files.c - identity hash + atomic write/copy round-trip tests.
 */
#include "aether_files/file_identity.h"
#include "aether_files/file_ops.h"
#include "aether_files/permission_check.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

static int checks = 0;
#define CHECK(cond)                                                         \
    do {                                                                    \
        if (!(cond)) {                                                      \
            fprintf(stderr, "FAIL %s:%d: %s\n", __FILE__, __LINE__, #cond); \
            return 1;                                                       \
        }                                                                   \
        checks++;                                                           \
    } while (0)

int main(void)
{
    char path[] = "/tmp/aether-files-test-XXXXXX";
    char copy_path[128];
    int fd = mkstemp(path);
    CHECK(fd >= 0);
    const char *content = "hello aether files";
    CHECK(write(fd, content, strlen(content)) == (ssize_t)strlen(content));
    close(fd);

    /* Identity is stable and changes with content metadata. */
    uint64_t id1 = aether_file_identity_path(path);
    CHECK(id1 != 0);
    CHECK(id1 == aether_file_identity_path(path));
    CHECK(aether_file_identity_path("/nonexistent/path/xyz") == 0);

    /* FNV-1a reference vector: hash of "a" = 0xaf63dc4c8601ec8c. */
    CHECK(aether_fnv1a64((const uint8_t *)"a", 1, AETHER_FNV1A_OFFSET) == 0xaf63dc4c8601ec8cULL);

    /* Atomic write. */
    snprintf(copy_path, sizeof(copy_path), "%s.copy", path);
    CHECK(aether_file_write_atomic(copy_path, (const uint8_t *)"second", 6) == 0);
    size_t len = 0;
    uint8_t *buf = aether_file_read_all(copy_path, 4096, &len);
    CHECK(buf != NULL && len == 6 && memcmp(buf, "second", 6) == 0);
    free(buf);

    /* Atomic copy of the original. */
    char copy2[128];
    snprintf(copy2, sizeof(copy2), "%s.copy2", path);
    CHECK(aether_file_copy_atomic(path, copy2) == 0);
    buf = aether_file_read_all(copy2, 4096, &len);
    CHECK(buf != NULL && len == strlen(content) && memcmp(buf, content, len) == 0);
    free(buf);
    CHECK(aether_file_copy_atomic("/nonexistent/src", copy2) != 0);

    /* Permission wrappers. */
    CHECK(aether_file_can(path, AETHER_PERM_READ) == true);
    CHECK(aether_file_owned_and(path, geteuid(), AETHER_PERM_READ) == true);
    CHECK(aether_file_owned_and(path, (uid_t)1, AETHER_PERM_READ) == false);
    CHECK(aether_file_is_regular(path) == true);
    CHECK(aether_file_is_dir(path) == false);
    CHECK(aether_file_free_bytes("/tmp") > 0);

    unlink(path);
    unlink(copy_path);
    unlink(copy2);
    printf("libaether-files: %d checks passed\n", checks);
    return 0;
}
