/* Permission checks before file actions (real access(2)+stat wrappers). */
#ifndef AETHER_FILES_PERMISSION_CHECK_H
#define AETHER_FILES_PERMISSION_CHECK_H
#include "aether_core/result.h"
#include <sys/types.h>
aether_result_t aether_file_permission_check(const char *path, int mode, uid_t uid, gid_t gid);
#endif
