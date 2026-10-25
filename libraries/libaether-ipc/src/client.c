#include "common.h"
/*
 * client.c - blocking framed unix-socket client implementation.
 */
#include "aether_ipc/client.h"
#include "aether_ipc/message_envelope.h"

#include <errno.h>
#include <stdlib.h>
#include <string.h>
#include <sys/socket.h>
#include <sys/un.h>
#include <unistd.h>

static int set_timeout(int fd, int timeout_ms)
{
    struct timeval tv;
    tv.tv_sec = timeout_ms / 1000;
    tv.tv_usec = (timeout_ms % 1000) * 1000;
    if (setsockopt(fd, SOL_SOCKET, SO_RCVTIMEO, &tv, sizeof(tv)) != 0) {
        return -1;
    }
    if (setsockopt(fd, SOL_SOCKET, SO_SNDTIMEO, &tv, sizeof(tv)) != 0) {
        return -1;
    }
    return 0;
}

int aipc_client_connect(aipc_client *client, const char *socket_path, int timeout_ms)
{
    struct sockaddr_un addr;

    if (client == NULL || socket_path == NULL || socket_path[0] == '\0') {
        return -1;
    }
    if (strlen(socket_path) >= sizeof(client->socket_path)) {
        return -1;
    }
    memset(client, 0, sizeof(*client));
    memcpy(client->socket_path, socket_path, strlen(socket_path));

    client->fd = socket(AF_UNIX, SOCK_STREAM, 0);
    if (client->fd < 0) {
        client->last_errno = errno;
        return -1;
    }
    if (timeout_ms > 0 && set_timeout(client->fd, timeout_ms) != 0) {
        client->last_errno = errno;
        close(client->fd);
        client->fd = -1;
        return -1;
    }
    memset(&addr, 0, sizeof(addr));
    addr.sun_family = AF_UNIX;
    memcpy(addr.sun_path, socket_path, strlen(socket_path));
    if (connect(client->fd, (struct sockaddr *)&addr, sizeof(addr)) != 0) {
        client->last_errno = errno;
        close(client->fd);
        client->fd = -1;
        return -1;
    }
    return 0;
}

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

static int read_all(int fd, uint8_t *buf, size_t len)
{
    size_t received = 0;
    while (received < len) {
        ssize_t n = recv(fd, buf + received, len - received, 0);
        if (n == 0) {
            return 1; /* clean close */
        }
        if (n < 0) {
            if (errno == EINTR) {
                continue;
            }
            return -1;
        }
        received += (size_t)n;
    }
    return 0;
}

int aipc_client_send(aipc_client *client, const uint8_t *payload, uint32_t payload_len)
{
    size_t frame_size = 0;
    uint8_t *frame = NULL;
    int rc;

    if (client == NULL || client->fd < 0) {
        return -1;
    }
    if (payload_len == 0) {
        return -1; /* empty payloads are not valid Aether IPC requests */
    }
    frame_size = AIPC_HEADER_SIZE + payload_len;
    frame = (uint8_t *)malloc(frame_size);
    if (frame == NULL) {
        return -1;
    }
    rc = aipc_envelope_encode(payload, payload_len, frame, frame_size, &frame_size);
    if (rc != 0) {
        free(frame);
        return -1;
    }
    rc = write_all(client->fd, frame, frame_size);
    free(frame);
    if (rc != 0) {
        client->last_errno = errno;
        return -1;
    }
    return 0;
}

long aipc_client_recv(aipc_client *client, uint8_t **out_buf, int timeout_ms)
{
    uint8_t header[AIPC_HEADER_SIZE];
    uint32_t payload_len = 0;
    uint8_t *buf = NULL;
    int rc;

    if (client == NULL || client->fd < 0 || out_buf == NULL) {
        return -1;
    }
    *out_buf = NULL;
    rc = read_all(client->fd, header, AIPC_HEADER_SIZE);
    if (rc != 0) {
        client->last_errno = errno;
        return rc == 1 ? 0 : -1;
    }
    if (aipc_envelope_decode_header(header, AIPC_HEADER_SIZE, &payload_len) != 0) {
        return -1;
    }
    if (payload_len == 0) {
        return -1;
    }
    buf = (uint8_t *)malloc(payload_len + 1);
    if (buf == NULL) {
        return -1;
    }
    rc = read_all(client->fd, buf, payload_len);
    if (rc != 0) {
        free(buf);
        client->last_errno = errno;
        return rc == 1 ? 0 : -1;
    }
    buf[payload_len] = '\0';
    *out_buf = buf;
    (void)timeout_ms;
    return (long)payload_len;
}

void aipc_client_close(aipc_client *client)
{
    if (client == NULL) {
        return;
    }
    if (client->fd >= 0) {
        close(client->fd);
        client->fd = -1;
    }
}
