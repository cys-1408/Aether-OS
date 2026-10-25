/* Deadline helpers. */
#ifndef AETHER_CORE_TIMEOUT_H
#define AETHER_CORE_TIMEOUT_H
#include <stdbool.h>
#include <time.h>

typedef struct { struct timespec deadline; } ct_deadline_t;
void ct_deadline_start(ct_deadline_t *d, unsigned timeout_ms);
bool ct_deadline_expired(const ct_deadline_t *d);
unsigned ct_deadline_remaining_ms(const ct_deadline_t *d);
#endif
