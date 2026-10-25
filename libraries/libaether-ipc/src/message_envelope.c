#include "common.h"
/*
 * message_envelope.c - AIP1 frame encode/decode.
 */
#include "aether_ipc/message_envelope.h"

void aipc_u32_store(uint8_t *dst, uint32_t value)
{
    dst[0] = (uint8_t)(value & 0xFFu);
    dst[1] = (uint8_t)((value >> 8) & 0xFFu);
    dst[2] = (uint8_t)((value >> 16) & 0xFFu);
    dst[3] = (uint8_t)((value >> 24) & 0xFFu);
}

uint32_t aipc_u32_load(const uint8_t *src)
{
    return (uint32_t)src[0] | ((uint32_t)src[1] << 8) |
           ((uint32_t)src[2] << 16) | ((uint32_t)src[3] << 24);
}

int aipc_envelope_encode(const uint8_t *payload, uint32_t payload_len,
                         uint8_t *buf, size_t buf_size, size_t *out_frame_size)
{
    if (out_frame_size != NULL) {
        *out_frame_size = 0;
    }
    if (payload == NULL && payload_len != 0) {
        return -1;
    }
    if (payload_len > AIPC_MAX_PAYLOAD) {
        return -1;
    }
    if (buf == NULL || buf_size < AIPC_HEADER_SIZE + payload_len) {
        return -1;
    }
    buf[0] = AIPC_MAGIC_0;
    buf[1] = AIPC_MAGIC_1;
    buf[2] = AIPC_MAGIC_2;
    buf[3] = AIPC_MAGIC_3;
    aipc_u32_store(buf + 4, payload_len);
    if (payload_len > 0) {
        for (uint32_t i = 0; i < payload_len; i++) {
            buf[AIPC_HEADER_SIZE + i] = payload[i];
        }
    }
    if (out_frame_size != NULL) {
        *out_frame_size = AIPC_HEADER_SIZE + payload_len;
    }
    return 0;
}

int aipc_envelope_decode_header(const uint8_t *buf, size_t buf_size,
                                uint32_t *payload_len)
{
    if (payload_len != NULL) {
        *payload_len = 0;
    }
    if (buf == NULL || buf_size < AIPC_HEADER_SIZE) {
        return -1;
    }
    if (buf[0] != AIPC_MAGIC_0 || buf[1] != AIPC_MAGIC_1 ||
        buf[2] != AIPC_MAGIC_2 || buf[3] != AIPC_MAGIC_3) {
        return -1;
    }
    uint32_t len = aipc_u32_load(buf + 4);
    if (len > AIPC_MAX_PAYLOAD) {
        return -2;
    }
    if (payload_len != NULL) {
        *payload_len = len;
    }
    return 0;
}
