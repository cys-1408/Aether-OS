/* Cooperative cancellation token (C11 atomics). */
#ifndef AETHER_CORE_CANCELLATION_H
#define AETHER_CORE_CANCELLATION_H
#include <stdatomic.h>
#include <stdbool.h>
#include <threads.h>

typedef struct { atomic_bool flag; } ct_cancel_t;

void ct_cancel_init(ct_cancel_t *c);
void ct_cancel(ct_cancel_t *c);
bool ct_cancelled(const ct_cancel_t *c);
/* Wait up to timeout_ms for cancellation; returns true if cancelled. */
bool ct_cancel_wait(ct_cancel_t *c, unsigned timeout_ms);
#endif
