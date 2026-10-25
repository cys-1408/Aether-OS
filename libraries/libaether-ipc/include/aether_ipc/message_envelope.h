/* Length-prefixed UTF-8 framing for the C IPC library.
 * Frame: u32 big-endian length + payload bytes (JSON handled by callers). */
#ifndef AETHER_IPC_MESSAGE_ENVELOPE_H
#define AETHER_IPC_MESSAGE_ENVELOPE_H
#include <stddef.h>
#include <stdint.h>

#define AETHER_IPC_MAX_FRAME (32u * 1024u * 1024u)

int aether_frame_encode(const uint8_t *payload, size_t len, uint8_t **out, size_t *out_len);
/* Returns 0 on success; consumes exactly one frame from buf. */
int aether_frame_decode(const uint8_t *buf, size_t buf_len,
                        const uint8_t **payload, size_t *payload_len,
                        size_t *consumed);
#endif
