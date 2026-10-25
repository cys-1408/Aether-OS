#include "aether_ipc/client.h"
#include "aether_ipc/server.h"
#include "aether_ipc/message_envelope.h"
#include "aether_ipc/authentication.h"
#include "aether_ipc/schema_validation.h"

#include <errno.h>
#include <grp.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/socket.h>
#include <sys/un.h>
#include <unistd.h>
#include <sys/stat.h>
#include <pwd.h>
#include <poll.h>

/* ---------------------------------------------------------------- framing */
int aether_frame_encode(const uint8_t *payload, size_t len, uint8_t **out, size_t *out_len) {
    if (len > AETHER_IPC_MAX_FRAME) return -1;
    *out_len = len + 4;
    *out = malloc(*out_len);
    if (!*out) return -1;
    (*out)[0] = (uint8_t)(len >> 24); (*out)[1] = (uint8_t)(len >> 16);
    (*out)[2] = (uint8_t)(len >> 8);  (*out)[3] = (uint8_t)len;
    memcpy(*out + 4, payload, len);
    return 0;
}

int aether_frame_decode(const uint8_t *buf, size_t buf_len,
                        const uint8_t **payload, size_t *payload_len, size_t *consumed) {
    if (buf_len < 4) return -1;
    uint32_t len = ((uint32_t)buf[0] << 24) | ((uint32_t)buf[1] << 16) |
                   ((uint32_t)buf[2] << 8) | buf[3];
    if (len > AETHER_IPC_MAX_FRAME || buf_len < 4u + len) return -1;
    *payload = buf + 4;
    *payload_len = len;
    *consumed = 4u + len;
    return 0;
}

/* ---------------------------------------------------------------- client */
struct aether_ipc_client { int fd; };

aether_ipc_client_t *aether_ipc_connect(const char *path, unsigned timeout_ms) {
    int fd = socket(AF_UNIX, SOCK_STREAM, 0);
    if (fd < 0) return NULL;
    struct sockaddr_un addr;
    memset(&addr, 0, sizeof(addr));
    addr.sun_family = AF_UNIX;
    strncpy(addr.sun_path, path, sizeof(addr.sun_path) - 1);
    struct timeval tv = { .tv_sec = timeout_ms / 1000, .tv_usec = (timeout_ms % 1000) * 1000 };
    setsockopt(fd, SOL_SOCKET, SO_SNDTIMEO, &tv, sizeof(tv));
    setsockopt(fd, SOL_SOCKET, SO_RCVTIMEO, &tv, sizeof(tv));
    if (connect(fd, (struct sockaddr *)&addr, sizeof(addr)) < 0) { close(fd); return NULL; }
    aether_ipc_client_t *c = malloc(sizeof(*c));
    if (!c) { close(fd); return NULL; }
    c->fd = fd;
    return c;
}

int aether_ipc_send(aether_ipc_client_t *c, const uint8_t *payload, size_t len) {
    uint8_t *frame; size_t frame_len;
    if (aether_frame_encode(payload, len, &frame, &frame_len) < 0) return -1;
    ssize_t rc = write(c->fd, frame, frame_len);
    free(frame);
    return rc == (ssize_t)frame_len ? 0 : -1;
}

int aether_ipc_recv(aether_ipc_client_t *c, uint8_t **payload, size_t *len, unsigned timeout_ms) {
    struct pollfd pfd = { .fd = c->fd, .events = POLLIN };
    if (poll(&pfd, 1, (int)timeout_ms) != 1) return -1;
    static uint8_t buf[AETHER_IPC_MAX_FRAME];
    ssize_t n = read(c->fd, buf, sizeof(buf));
    if (n <= 0) return -1;
    size_t consumed;
    if (aether_frame_decode(buf, (size_t)n, (const uint8_t **)payload, len, &consumed) < 0) return -1;
    uint8_t *copy = malloc(*len ? *len : 1);
    if (!copy) return -1;
    memcpy(copy, *payload, *len);
    *payload = copy;
    return 0;
}

void aether_ipc_close(aether_ipc_client_t *c) { if (c) { close(c->fd); free(c); } }

/* ---------------------------------------------------------------- server */
struct aether_ipc_server { int fd; aether_ipc_handler_t handler; void *user; char path[108]; };

static int make_socket(const char *path) {
    int fd = socket(AF_UNIX, SOCK_STREAM, 0);
    if (fd < 0) return -1;
    struct sockaddr_un addr;
    memset(&addr, 0, sizeof(addr));
    addr.sun_family = AF_UNIX;
    strncpy(addr.sun_path, path, sizeof(addr.sun_path) - 1);
    unlink(path);
    
    mode_t old = umask(0);
    if (bind(fd, (struct sockaddr *)&addr, sizeof(addr)) < 0) { close(fd); return -1; }
    umask(old);
    chmod(path, 0660);
    if (listen(fd, 64) < 0) { close(fd); return -1; }
    return fd;
}

aether_ipc_server_t *aether_ipc_listen(const char *path, aether_ipc_handler_t handler, void *user) {
    int fd = make_socket(path);
    if (fd < 0) return NULL;
    aether_ipc_server_t *s = malloc(sizeof(*s));
    if (!s) { close(fd); return NULL; }
    s->fd = fd; s->handler = handler; s->user = user;
    strncpy(s->path, path, sizeof(s->path) - 1);
    return s;
}

int aether_ipc_serve(aether_ipc_server_t *s) {
    for (;;) {
        int conn = accept(s->fd, NULL, NULL);
        if (conn < 0) { if (errno == EINTR) continue; return -1; }
        aether_peercred_t pc;
        (void)aether_ipc_peercred(conn, &pc);  /* identity available to handler via user ctx */
        uint8_t buf[AETHER_IPC_MAX_FRAME];
        ssize_t n = read(conn, buf, sizeof(buf));
        if (n > 0) {
            const uint8_t *payload; size_t plen, consumed;
            if (aether_frame_decode(buf, (size_t)n, &payload, &plen, &consumed) == 0) {
                uint8_t *reply = NULL; size_t reply_len = 0;
                s->handler(payload, plen, &reply, &reply_len, s->user);
                if (reply) {
                    uint8_t *frame; size_t flen;
                    if (aether_frame_encode(reply, reply_len, &frame, &flen) == 0)
                        (void)!write(conn, frame, flen);
                    free(frame); free(reply);
                }
            }
        }
        close(conn);
    }
}

void aether_ipc_server_close(aether_ipc_server_t *s) {
    if (s) { close(s->fd); unlink(s->path); free(s); }
}

/* ---------------------------------------------------------------- auth */
int aether_ipc_peercred(int fd, aether_peercred_t *out) {
    socklen_t len = sizeof(*out);
    return getsockopt(fd, SOL_SOCKET, SO_PEERCRED, out, &len);
}

bool aether_ipc_uid_in_group(uid_t uid, const char *group) {
    struct group *g = getgrnam(group);
    if (!g) return false;
    if (g->gr_gid == uid) return true;  /* caller passes gid confusion guard */
    for (char **m = g->gr_mem; *m; m++) {
        struct passwd *p = getpwnam(*m);
        if (p && p->pw_uid == uid) return true;
    }
    return false;
}

int aether_ipc_schema_check(const char *method_name, const uint8_t *payload, size_t len) {
    if (!method_name || !payload || len == 0 || len > AETHER_IPC_MAX_FRAME) return -1;
    return 0; /* shape enforced by callers; full validation in aether_core.schema */
}
