#ifndef AETHER_IPC_SCHEMA_VALIDATION_H
#define AETHER_IPC_SCHEMA_VALIDATION_H
#include <stddef.h>
/* Minimal structural check hook point: full JSON Schema validation lives in
 * aether_core.schema (Python). C callers delegate or enforce shape before send. */
int aether_ipc_schema_check(const char *method_name, const uint8_t *payload, size_t len);
#endif
