#include "aether_ui/theme.h"
#include <stdbool.h>
#include <string.h>

/* Motion tokens (seconds) and their reduced-motion equivalents. */
typedef struct { const char *name; double normal_s; double reduced_s; } aether_motion_t;
static const aether_motion_t MOTION[] = {
    { "tail", 2.0, 0.0 }, { "head", 5.0, 0.0 }, { "walk_bob", 0.5, 0.0 },
    { "jump", 0.65, 0.0 }, { "panel", 0.25, 0.0 }, { "window", 0.6, 0.0 },
    { "toast", 2.6, 0.0 }, { "bubble", 3.0, 0.0 }, { NULL, 0.0, 0.0 }
};

double aether_ui_motion_seconds(const char *name, bool reduced) {
    for (int i = 0; MOTION[i].name; i++)
        if (strcmp(MOTION[i].name, name) == 0) return reduced ? MOTION[i].reduced_s : MOTION[i].normal_s;
    return 0.0;
}
