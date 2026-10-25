/* Versioned key=value config store with atomic replace. */
#ifndef AETHER_CONFIG_STORE_H
#define AETHER_CONFIG_STORE_H
#include "aether_core/result.h"

aether_result_t aether_config_read(const char *path, const char *key, char *out, size_t out_max);
aether_result_t aether_config_write(const char *path, const char *key, const char *value);
aether_result_t aether_config_get_version(const char *path, unsigned *version);
#endif
