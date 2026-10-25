#include "aether_core/result.h"
#include <stdio.h>
#include <string.h>

aether_result_t aether_ok(void) {
    aether_result_t r = { .ok = true, .code = AE_OK, .message = {0} };
    return r;
}

aether_result_t aether_err(int code, const char *message) {
    aether_result_t r = { .ok = false, .code = code, .message = {0} };
    if (message) {
        strncpy(r.message, message, AETHER_MSG_MAX - 1);
        r.message[AETHER_MSG_MAX - 1] = '\0';
    }
    return r;
}
