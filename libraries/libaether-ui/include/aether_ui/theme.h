/* Theme token table (mirrors desktop/theme/palette.yaml + CONVENTIONS §9). */
#ifndef AETHER_UI_THEME_H
#define AETHER_UI_THEME_H
typedef struct { const char *name; const char *hex; } aether_theme_token_t;
extern const aether_theme_token_t AETHER_THEME[];
const char *aether_theme_hex(const char *name);
#endif
