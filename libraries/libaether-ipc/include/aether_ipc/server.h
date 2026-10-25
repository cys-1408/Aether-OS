#ifndef AETHER_IPC_SERVER_H
#define AETHER_IPC_SERVER_H
#include <stddef.h>
#include <stdint.h>

typedef struct aether_ipc_server aether_ipc_server_t;
typedef void (*aether_ipc_handler_t)(const uint8_t *payload, size_t len,
                                     uint8_t **reply, size_t *reply_len, void *user);

aether_ipc_server_t *aether_ipc_listen(const char *path, aether_ipc_handler_t handler, void *user);
/* Blocking accept loop; returns -1 on fatal error. */
int aether_ipc_serve(aether_ipc_server_t *s);
void aether_ipc_server_close(aether_ipc_server_t *s);
#endif
