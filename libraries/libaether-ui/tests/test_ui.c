/*
 * test_ui.c - theme tokens + focus order + reduced motion tests.
 */
#include "aether_ui/theme.h"
#include "aether_ui/accessibility.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static int checks = 0;
#define CHECK(cond)                                                         \
    do {                                                                    \
        if (!(cond)) {                                                      \
            fprintf(stderr, "FAIL %s:%d: %s\n", __FILE__, __LINE__, #cond); \
            return 1;                                                       \
        }                                                                   \
        checks++;                                                           \
    } while (0)

int main(void)
{
    size_t count = 0;
    const aether_theme_token_t *tokens = aether_theme_tokens(&count);
    CHECK(count == 7);
    CHECK(strcmp(aether_theme_token("ink"), "#292824") == 0);
    CHECK(strcmp(aether_theme_token("orange"), "#d98250") == 0);
    CHECK(strcmp(aether_theme_token("blue"), "#8fa9c4") == 0);
    CHECK(aether_theme_token("nope") == NULL);

    size_t surface_count = 0;
    const aether_theme_token_t *surfaces = aether_theme_surfaces(&surface_count);
    CHECK(surface_count == 25);
    CHECK(strcmp(aether_theme_token("terminal_bg"), "#262a30") == 0);
    CHECK(strcmp(aether_theme_token("dot_max"), "#28ca41") == 0);
    (void)tokens; (void)surfaces;

    CHECK(aether_theme_motion_window_ms() == 600);
    CHECK(aether_theme_motion_toast_ms() == 2600);

    /* Focus order. */
    aether_focus_order_t order;
    memset(&order, 0, sizeof(order));
    CHECK(aether_focus_register(&order, "btn-open", 0, 0));
    CHECK(aether_focus_register(&order, "btn-save", 0, 1));
    CHECK(aether_focus_register(&order, "btn-close", 1, 0));
    CHECK(strcmp(aether_focus_next(&order, "btn-open"), "btn-save") == 0);
    CHECK(strcmp(aether_focus_next(&order, "btn-close"), "btn-open") == 0); /* wraps */
    CHECK(strcmp(aether_focus_previous(&order, "btn-open"), "btn-close") == 0);
    CHECK(strcmp(aether_focus_arrow(&order, "btn-open", 0, 1), "btn-close") == 0);
    CHECK(strcmp(aether_focus_arrow(&order, "btn-open", 1, 0), "btn-save") == 0);
    CHECK(aether_focus_arrow(&order, "btn-save", 1, 0) == NULL); /* nothing right of column 1 */
    CHECK(aether_focus_next(&order, "ghost") != NULL); /* unknown starts at head */

    /* Reduced motion: env contract. */
    setenv("AETHER_REDUCED_MOTION", "1", 1);
    CHECK(aether_ui_reduced_motion_enabled() == true);
    setenv("AETHER_REDUCED_MOTION", "0", 1);
    CHECK(aether_ui_reduced_motion_enabled() == false);
    unsetenv("AETHER_REDUCED_MOTION");
    aether_ui_set_reduced_motion_override(1);
    CHECK(aether_ui_reduced_motion_enabled() == true);
    aether_ui_set_reduced_motion_override(-1);

    printf("libaether-ui: %d checks passed\n", checks);
    return 0;
}
