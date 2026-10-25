#ifndef AETHER_IPC_AUTHENTICATION_H
#define AETHER_IPC_AUTHENTICATION_H
#include <stdbool.h>
#include <sys/types.h>
/* SO_PEERCRED identity of the peer on a connected fd. */
typedef struct { pid_t pid; uid_t uid; gid_t gid; } aether_peercred_t;
int aether_ipc_peercred(int fd, aether_peercred_t *out);
bool aether_ipc_uid_in_group(uid_t uid, const char *group);
#endif
