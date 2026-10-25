#ifndef AETHER_IPC_CLIENT_H
#define AETHER_IPC_CLIENT_H
#include <stddef.h>
#include <stdint.h>

typedef struct aether_ipc_client aether_ipc_client_t;
/* Connect to a unix socket at path. NULL on error. */
aether_ipc_client_t *aether_ipc_connect(const char *path, unsigned timeout_ms);
/* Send one framed request payload; returns 0 or -1. */
int aether_ipc_send(aether_ipc_client_t *c, const uint8_t *payload, size_t len);
/* Receive one framed reply payload; caller frees *payload. */
int aether_ipc_recv(aether_ipc_client_t *c, uint8_t **payload, size_t *len, unsigned timeout_ms);
void aether_ipc_close(aether_ipc_client_t *c);
#endif
