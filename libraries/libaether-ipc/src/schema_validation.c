#include "common.h"
/*
 * schema_validation.c - UTF-8 + payload contract checks.
 */
#include "aether_ipc/schema_validation.h"
#include "aether_ipc/message_envelope.h"

#include <stdio.h>
#include <string.h>

static void fill_reason(char *reason, unsigned reason_size, const char *text)
{
    unsigned i;
    if (reason == NULL || reason_size == 0) {
        return;
    }
    for (i = 0; text[i] != '\0' && i + 1 < reason_size; i++) {
        reason[i] = text[i];
    }
    reason[i] = '\0';
}

bool aipc_utf8_valid(const uint8_t *data, size_t len)
{
    size_t i = 0;

    while (i < len) {
        uint8_t b = data[i];
        uint32_t codepoint;
        size_t extra;

        if (b <= 0x7Fu) {
            i++;
            continue;
        }
        if ((b & 0xE0u) == 0xC0u) {
            extra = 1;
            codepoint = b & 0x1Fu;
        } else if ((b & 0xF0u) == 0xE0u) {
            extra = 2;
            codepoint = b & 0x0Fu;
        } else if ((b & 0xF8u) == 0xF0u) {
            extra = 3;
            codepoint = b & 0x07u;
        } else {
            return false; /* 0x80..0xBF or 0xF8..0xFF: never valid as lead */
        }
        if (i + extra >= len) { /* need one more byte than continuation count */
            return false;
        }
        for (size_t k = 1; k <= extra; k++) {
            uint8_t cont = data[i + k];
            if ((cont & 0xC0u) != 0x80u) {
                return false;
            }
            codepoint = (codepoint << 6) | (cont & 0x3Fu);
        }
        /* Reject overlong encodings, surrogates and > U+10FFFF. */
        if (extra == 1 && codepoint < 0x80u) {
            return false;
        }
        if (extra == 2 && codepoint < 0x800u) {
            return false;
        }
        if (extra == 3 && codepoint < 0x10000u) {
            return false;
        }
        if (codepoint >= 0xD800u && codepoint <= 0xDFFFu) {
            return false;
        }
        if (codepoint > 0x10FFFFu) {
            return false;
        }
        i += extra + 1;
    }
    return true;
}

bool aipc_payload_valid(const uint8_t *payload, size_t len, char *reason, unsigned reason_size)
{
    if (payload == NULL || len == 0) {
        fill_reason(reason, reason_size, "payload is empty");
        return false;
    }
    if (len > AIPC_MAX_PAYLOAD) {
        char too_large[64];
        snprintf(too_large, sizeof(too_large), "payload exceeds %u bytes", (unsigned)AIPC_MAX_PAYLOAD);
        fill_reason(reason, reason_size, too_large);
        return false;
    }
    if (!aipc_utf8_valid(payload, len)) {
        fill_reason(reason, reason_size, "payload is not valid UTF-8");
        return false;
    }
    if (reason != NULL && reason_size > 0) {
        reason[0] = '\0';
    }
    return true;
}
