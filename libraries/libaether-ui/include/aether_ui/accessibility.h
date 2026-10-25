#ifndef AETHER_UI_ACCESSIBILITY_H
#define AETHER_UI_ACCESSIBILITY_H
#include "aether_core/result.h"
double aether_ui_motion_seconds(const char *name, int reduced);
aether_result_t aether_ui_keyboard_policy(int *focus_visible_default);
#endif
