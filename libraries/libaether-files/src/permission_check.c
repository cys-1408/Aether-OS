#include "aether_core/result.h"
#include <unistd.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <errno.h>
#include <string.h>

/* Query real filesystem permissions before acting. */
aether_result_t aether_file_permission_check(const char *path, int mode, uid_t uid, gid_t gid) {
    struct stat st;
    if (stat(path, &st) < 0) return aether_err(AE_NOT_FOUND, strerror(errno));
    if (uid == st.st_uid) {
        if ((mode & R_OK) && !(st.st_mode & S_IRUSR)) return aether_err(E_DENIED, "owner read denied");
        if ((mode & W_OK) && !(st.st_mode & S_IWUSR)) return aether_err(E_DENIED, "owner write denied");
    }
    if (access(path, mode) < 0) return aether_err(E_DENIED, strerror(errno));
    (void)gid;
    return aether_ok();
}
