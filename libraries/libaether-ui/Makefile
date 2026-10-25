# libaether-ui — Makefile
DESTDIR   ?=
PREFIX    ?= /usr
BUILD_DIR = build

SOURCES = src/theme.c src/keyboard_navigation.c src/reduced_motion.c
OBJECTS = $(patsubst src/%.c,$(BUILD_DIR)/%.o,$(SOURCES))

CFLAGS  ?= -std=c11 -Wall -Wextra -O2
CPPFLAGS += -Iinclude -Isrc -D_GNU_SOURCE -D_POSIX_C_SOURCE=200809L -D_DEFAULT_SOURCE

.PHONY: all test install uninstall clean

all: $(BUILD_DIR)/libaether_ui.a

$(BUILD_DIR)/libaether_ui.a: $(OBJECTS)
	ar rcs $@ $^

$(BUILD_DIR)/%.o: src/%.c
	$(CC) $(CFLAGS) $(CPPFLAGS) -c $< -o $@

test: $(BUILD_DIR)/libaether_ui.a
	$(CC) $(CFLAGS) $(CPPFLAGS) tests/test_ui.c -o $(BUILD_DIR)/test_ui $(BUILD_DIR)/libaether_ui.a -lm
	$(BUILD_DIR)/test_ui

install: all
	install -d $(DESTDIR)$(PREFIX)/lib $(DESTDIR)$(PREFIX)/include/aether_ui
	install -m 0644 $(BUILD_DIR)/libaether_ui.a $(DESTDIR)$(PREFIX)/lib/
	install -m 0644 include/aether_ui/*.h $(DESTDIR)$(PREFIX)/include/aether_ui/

uninstall:
	rm -f $(DESTDIR)$(PREFIX)/lib/libaether_ui.a
	rm -rf $(DESTDIR)$(PREFIX)/include/aether_ui

clean:
	rm -rf $(BUILD_DIR)
