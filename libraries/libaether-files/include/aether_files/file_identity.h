/* Stable file identity: FNV-1a of dev:ino:size:mtime. */
#ifndef AETHER_FILES_FILE_IDENTITY_H
#define AETHER_FILES_FILE_IDENTITY_H
#include "aether_core/result.h"
aether_result_t aether_file_identity(const char *path, char *out, size_t out_max);
#endif
