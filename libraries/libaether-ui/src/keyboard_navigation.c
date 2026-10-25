#include "aether_core/result.h"
#include <stdbool.h>

/* Shared keyboard-navigation policy for native UI components:
 * - every focusable widget participates in one ring order
 * - Escape closes, Enter/Space activates, arrows move within lists */
aether_result_t aether_ui_keyboard_policy(bool *focus_visible_default) {
    *focus_visible_default = true;
    return aether_ok();
}
