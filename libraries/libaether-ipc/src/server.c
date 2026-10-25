#include "common.h"
/*
 * server.c - framed unix-socket server implementation.
 */
#include "aether_ipc/server.h"
#include "aether_ipc/authentication.h"
#include "aether_ipc/message_envelope.h"
#include "aether_ipc/schema_validation.h"

#include <errno.h>
#include <grp.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include <sys/socket.h>
#include <sys/stat.h>
#include <sys/un.h>
#include <unistd.h>

/* Transport-level failure marker: valid frame, payload "-1". */
static const uint8_t AIPC_ERR_FRAME[AIPC_HEADER_SIZE + 2] = {
    AIPC_MAGIC_0, AIPC_MAGIC_1, AIPC_MAGIC_2, AIPC_MAGIC_3,
    0x02, 0x00, 0x00, 0x00,
    '-', '1'
};

typedef struct aipc_worker_arg {
    aipc_server *server;
    int fd;
} aipc_worker_arg_t;

static int write_all(int fd, const uint8_t *buf, size_t len)
{
    size_t sent = 0;
    while (sent < len) {
        ssize_t n = send(fd, buf + sent, len - sent, MSG_NOSIGNAL);
        if (n < 0) {
            if (errno == EINTR) {
                continue;
            }
            return -1;
        }
        sent += (size_t)n;
    }
    return 0;
}

/* Read one full frame from fd. Returns 0 ok, 1 clean close, -1 error. */
static int read_frame(int fd, uint8_t **payload, uint32_t *payload_len)
{
    uint8_t header[AIPC_HEADER_SIZE];
    uint8_t *buf;
    size_t received = 0;

    while (received < AIPC_HEADER_SIZE) {
        ssize_t n = recv(fd, header + received, AIPC_HEADER_SIZE - received, 0);
        if (n == 0) {
            return 1;
        }
        if (n < 0) {
            if (errno == EINTR) {
                continue;
            }
            return -1;
        }
        received += (size_t)n;
    }
    if (aipc_envelope_decode_header(header, AIPC_HEADER_SIZE, payload_len) != 0) {
        return -1;
    }
    if (*payload_len == 0) {
        return -1;
    }
    buf = (uint8_t *)malloc((size_t)*payload_len + 1);
    if (buf == NULL) {
        return -1;
    }
    received = 0;
    while (received < *payload_len) {
        ssize_t n = recv(fd, buf + received, *payload_len - received, 0);
        if (n == 0) {
            free(buf);
            return 1;
        }
        if (n < 0) {
            if (errno == EINTR) {
                continue;
            }
            free(buf);
            return -1;
        }
        received += (size_t)n;
    }
    buf[*payload_len] = '\0';
    *payload = buf;
    return 0;
}

static void *worker(void *opaque)
{
    aipc_worker_arg_t *arg = (aipc_worker_arg_t *)opaque;
    aipc_server *server = arg->server;
    int fd = arg->fd;
    uint8_t *request = NULL;
    uint32_t request_len = 0;
    uint8_t *response = NULL;
    size_t response_len = 0;
    char reason[128];
    aipc_peer_cred_t cred;
    int hrc;

    if (aipc_get_peer_cred(fd, &cred) == 0) {
        if (cred.uid != 0 && !aipc_uid_allowed(cred.uid, getegid())) {
            (void)write_all(fd, AIPC_ERR_FRAME, sizeof(AIPC_ERR_FRAME));
            close(fd);
            free(arg);
            return NULL;
        }
    }

    if (read_frame(fd, &request, &request_len) != 0) {
        close(fd);
        free(arg);
        return NULL;
    }
    if (!aipc_payload_valid(request, request_len, reason, sizeof(reason))) {
        (void)write_all(fd, AIPC_ERR_FRAME, sizeof(AIPC_ERR_FRAME));
        free(request);
        close(fd);
        free(arg);
        return NULL;
    }

    hrc = server->handler(request, request_len, &response, &response_len, server->user_data);
    if (hrc == 0 && response != NULL && response_len > 0) {
        size_t frame_size = AIPC_HEADER_SIZE + response_len;
        uint8_t *frame = (uint8_t *)malloc(frame_size);
        if (frame != NULL) {
            if (aipc_envelope_encode(response, (uint32_t)response_len, frame, frame_size, &frame_size) == 0) {
                (void)write_all(fd, frame, frame_size);
            }
            free(frame);
        }
        free(response);
    } else {
        (void)write_all(fd, AIPC_ERR_FRAME, sizeof(AIPC_ERR_FRAME));
    }

    free(request);
    close(fd);
    free(arg);
    return NULL;
}

int aipc_server_bind(aipc_server *server, const char *socket_path,
                     unsigned socket_mode, const char *group_name,
                     aipc_handler_fn handler, void *user_data)
{
    struct sockaddr_un addr;
    mode_t old_umask;
    struct stat st;

    if (server == NULL || socket_path == NULL || handler == NULL) {
        return -1;
    }
    if (strlen(socket_path) >= sizeof(server->socket_path)) {
        return -1;
    }
    memset(server, 0, sizeof(*server));
    server->listen_fd = -1;
    server->running = 0;
    memcpy(server->socket_path, socket_path, strlen(socket_path));
    server->handler = handler;
    server->user_data = user_data;
    pthread_mutex_init(&server->threads_lock, NULL);

    if (lstat(socket_path, &st) == 0 && S_ISSOCK(st.st_mode)) {
        unlink(socket_path); /* stale socket from a dead daemon */
    }

    old_umask = umask(0117);
    server->listen_fd = socket(AF_UNIX, SOCK_STREAM, 0);
    if (server->listen_fd < 0) {
        umask(old_umask);
        return -1;
    }
    memset(&addr, 0, sizeof(addr));
    addr.sun_family = AF_UNIX;
    memcpy(addr.sun_path, socket_path, strlen(socket_path));
    if (bind(server->listen_fd, (struct sockaddr *)&addr, sizeof(addr)) != 0) {
        umask(old_umask);
        close(server->listen_fd);
        server->listen_fd = -1;
        return -1;
    }
    umask(old_umask);

    if (chmod(socket_path, (mode_t)socket_mode) != 0) {
        close(server->listen_fd);
        server->listen_fd = -1;
        unlink(socket_path);
        return -1;
    }
    if (group_name != NULL && group_name[0] != '\0') {
        struct group *gr = getgrnam(group_name);
        if (gr != NULL) {
            /* Non-fatal when chown fails: the process primary group still applies. */
            (void)chown(socket_path, (uid_t)-1, gr->gr_gid);
        }
    }
    if (listen(server->listen_fd, 64) != 0) {
        close(server->listen_fd);
        server->listen_fd = -1;
        unlink(socket_path);
        return -1;
    }
    return 0;
}

int aipc_server_serve(aipc_server *server)
{
    if (server == NULL || server->listen_fd < 0) {
        return -1;
    }
    server->running = 1;
    while (server->running) {
        int fd = accept(server->listen_fd, NULL, NULL);
        aipc_worker_arg_t *arg;
        pthread_t thread;

        if (fd < 0) {
            if (errno == EINTR) {
                continue;
            }
            if (!server->running) {
                break;
            }
            return -1;
        }
        arg = (aipc_worker_arg_t *)malloc(sizeof(*arg));
        if (arg == NULL) {
            close(fd);
            continue;
        }
        arg->server = server;
        arg->fd = fd;
        if (pthread_create(&thread, NULL, worker, arg) == 0) {
            pthread_detach(thread);
        } else {
            close(fd);
            free(arg);
        }
    }
    return 0;
}

void aipc_server_stop(aipc_server *server)
{
    if (server == NULL) {
        return;
    }
    server->running = 0;
    if (server->listen_fd >= 0) {
        shutdown(server->listen_fd, SHUT_RDWR);
        close(server->listen_fd);
        server->listen_fd = -1;
    }
    unlink(server->socket_path);
    pthread_mutex_lock(&server->threads_lock);
    free(server->threads);
    server->threads = NULL;
    server->thread_count = 0;
    server->thread_capacity = 0;
    pthread_mutex_unlock(&server->threads_lock);
    pthread_mutex_destroy(&server->threads_lock);
}
