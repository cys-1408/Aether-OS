#ifndef AETHER_FILES_FILE_OPS_H
#define AETHER_FILES_FILE_OPS_H
#include "aether_core/result.h"
/* Atomic copy with fsync (tmp file in dest dir + rename). */
aether_result_t aether_file_copy_atomic(const char *src, const char *dst);
#endif
