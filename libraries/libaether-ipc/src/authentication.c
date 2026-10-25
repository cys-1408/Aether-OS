#include "common.h"
/*
 * authentication.c - SO_PEERCRED + group membership.
 */
#include "aether_ipc/authentication.h"

#include <errno.h>
#include <grp.h>
#include <limits.h>
#include <pwd.h>
#include <string.h>
#include <sys/socket.h>
#include <unistd.h>

int aipc_get_peer_cred(int fd, aipc_peer_cred_t *out)
{
    struct ucred cred;
    socklen_t len = sizeof(cred);

    if (out == NULL || fd < 0) {
        return -1;
    }
    if (getsockopt(fd, SOL_SOCKET, SO_PEERCRED, &cred, &len) != 0) {
        return -1;
    }
    if (len != sizeof(cred)) {
        return -1;
    }
    out->pid = cred.pid;
    out->uid = cred.uid;
    out->gid = cred.gid;
    return 0;
}

bool aipc_uid_allowed(uid_t uid, gid_t gid)
{
    if (uid == geteuid()) {
        return true;
    }
    return aipc_uid_in_group(uid, gid);
}

bool aipc_uid_in_group(uid_t uid, gid_t gid)
{
    struct passwd *pwd = getpwuid(uid);
    struct group *grp;
    char *const *member;
    gid_t supplementary[NGROUPS_MAX];
    int count = (int)(sizeof(supplementary) / sizeof(supplementary[0]));

    if (pwd == NULL) {
        return false;
    }
    grp = getgrgid(gid);
    if (grp == NULL) {
        return false;
    }
    if (pwd->pw_gid == gid) {
        return true;
    }
    for (member = grp->gr_mem; member != NULL && *member != NULL; member++) {
        if (strcmp(*member, pwd->pw_name) == 0) {
            return true;
        }
    }
    count = getgrouplist(pwd->pw_name, pwd->pw_gid, supplementary, &count);
    for (int i = 0; i < count; i++) {
        if (supplementary[i] == gid) {
            return true;
        }
    }
    return false;
}
