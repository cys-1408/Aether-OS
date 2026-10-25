#include "aether_core/result.h"
#include "aether_core/cancellation.h"
#include <assert.h>
#include <string.h>
#include <stdio.h>

int main(void) {
    aether_result_t ok = aether_ok();
    assert(ok.ok && ok.code == AE_OK);
    aether_result_t e = aether_err(AE_TIMEOUT, "too slow");
    assert(!e.ok && e.code == AE_TIMEOUT && strcmp(e.message, "too slow") == 0);
    ct_cancel_t c; ct_cancel_init(&c);
    assert(!ct_cancelled(&c));
    ct_cancel(&c);
    assert(ct_cancelled(&c));
    assert(ct_cancel_wait(&c, 5));
    puts("test_core: all assertions passed");
    return 0;
}
