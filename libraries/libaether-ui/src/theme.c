#include "aether_ui/theme.h"
#include <stddef.h>
#include <string.h>

const aether_theme_token_t AETHER_THEME[] = {
    { "ink", "#292824" }, { "muted", "#817b70" }, { "paper", "#fffdf8" },
    { "line", "#e8e1d6" }, { "orange", "#d98250" }, { "green", "#7c9080" },
    { "blue", "#8fa9c4" }, { "terminal_bg", "#262a30" }, { NULL, NULL }
};

const char *aether_theme_hex(const char *name) {
    for (int i = 0; AETHER_THEME[i].name; i++)
        if (strcmp(AETHER_THEME[i].name, name) == 0) return AETHER_THEME[i].hex;
    return NULL;
}
