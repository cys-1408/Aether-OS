/* Typed success/failure results (C11) — mirrors aether_core.result. */
#ifndef AETHER_CORE_RESULT_H
#define AETHER_CORE_RESULT_H

#include <stdbool.h>
#include <stddef.h>

#define AETHER_MSG_MAX 256

typedef struct {
    bool ok;
    int code;                       /* 0 on success; Aether E_* codes on failure */
    char message[AETHER_MSG_MAX];
} aether_result_t;

aether_result_t aether_ok(void);
aether_result_t aether_err(int code, const char *message);

/* Canonical error codes */
enum {
    AE_OK = 0,
    AE_INVALID = 1,
    AE_NOT_FOUND = 2,
    E_DENIED = 3,
    AE_TIMEOUT = 4,
    AE_IO = 5,
    AE_BUSY = 6,
    AE_UNSUPPORTED = 7,
    AE_CANCELLED = 8
};

#endif /* AETHER_CORE_RESULT_H */
