/*
 * test_ipc.c - round-trip test: envelope encode/decode + UTF-8 validation.
 */
#include "aether_ipc/message_envelope.h"
#include "aether_ipc/schema_validation.h"

#include <stdio.h>
#include <string.h>
#include <stdlib.h>

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
    uint8_t frame[AIPC_HEADER_SIZE + 64];
    size_t frame_size = 0;
    uint32_t decoded_len = 0;
    const char *payload = "{\"jsonrpc\":\"2.0\"}";

    CHECK(aipc_envelope_encode((const uint8_t *)payload, (uint32_t)strlen(payload),
                               frame, sizeof(frame), &frame_size) == 0);
    CHECK(frame_size == AIPC_HEADER_SIZE + strlen(payload));
    CHECK(aipc_envelope_decode_header(frame, frame_size, &decoded_len) == 0);
    CHECK(decoded_len == strlen(payload));
    CHECK(memcmp(frame + AIPC_HEADER_SIZE, payload, decoded_len) == 0);

    /* Bad magic must be rejected. */
    frame[1] = 'X';
    CHECK(aipc_envelope_decode_header(frame, frame_size, &decoded_len) == -1);
    frame[1] = AIPC_MAGIC_1;

    /* Oversized declared length must be rejected. */
    frame[4] = 0xFF; frame[5] = 0xFF; frame[6] = 0xFF; frame[7] = 0xFF;
    CHECK(aipc_envelope_decode_header(frame, frame_size, &decoded_len) == -2);

    /* UTF-8 validation. */
    CHECK(aipc_utf8_valid((const uint8_t *)"ascii only", 10) == true);
    CHECK(aipc_utf8_valid((const uint8_t *)"\xE6\x97\xA5\xE6\x9C\xAC", 6) == true); /* CJK */
    CHECK(aipc_utf8_valid((const uint8_t *)"\xC3", 1) == false);                    /* truncated */
    CHECK(aipc_utf8_valid((const uint8_t *)"\xC0\x80", 2) == false);                /* overlong */
    CHECK(aipc_utf8_valid((const uint8_t *)"\xED\xA0\x80", 3) == false);            /* surrogate */
    CHECK(aipc_utf8_valid((const uint8_t *)"\xF4\x90\x80\x80", 4) == false);        /* > U+10FFFF */
    CHECK(aipc_payload_valid((const uint8_t *)payload, strlen(payload), NULL, 0) == true);
    CHECK(aipc_payload_valid(NULL, 0, NULL, 0) == false);

    printf("libaether-ipc: %d checks passed\n", checks);
    return 0;
}
