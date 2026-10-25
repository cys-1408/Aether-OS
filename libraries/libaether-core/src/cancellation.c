#include "aether_core/cancellation.h"
#include <time.h>
#include <string.h>
#include <stdio.h>

void ct_cancel_init(ct_cancel_t *c) { atomic_init(&c->flag, false); }
void ct_cancel(ct_cancel_t *c) { atomic_store(&c->flag, true); }
bool ct_cancelled(const ct_cancel_t *c) { return atomic_load(&c->flag); }

bool ct_cancel_wait(ct_cancel_t *c, unsigned timeout_ms) {
    struct timespec ts;
    for (unsigned waited = 0; waited < timeout_ms; waited += 10) {
        if (atomic_load(&c->flag)) return true;
        ts.tv_sec = 0; ts.tv_nsec = 10 * 1000 * 1000;
        nanosleep(&ts, NULL);
    }
    return atomic_load(&c->flag);
}
