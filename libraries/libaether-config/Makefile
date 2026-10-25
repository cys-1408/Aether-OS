# libaether-config — Makefile
DESTDIR   ?=
PREFIX    ?= /usr
BUILD_DIR = build

SOURCES = src/config_store.c src/config_migration.c
OBJECTS = $(patsubst src/%.c,$(BUILD_DIR)/%.o,$(SOURCES))

CFLAGS  ?= -std=c11 -Wall -Wextra -O2
CPPFLAGS += -Iinclude -Isrc -D_GNU_SOURCE -D_POSIX_C_SOURCE=200809L -D_DEFAULT_SOURCE

.PHONY: all test install uninstall clean

all: $(BUILD_DIR)/libaether_config.a

$(BUILD_DIR)/libaether_config.a: $(OBJECTS)
	ar rcs $@ $^

$(BUILD_DIR)/%.o: src/%.c
	$(CC) $(CFLAGS) $(CPPFLAGS) -c $< -o $@

test: $(BUILD_DIR)/libaether_config.a
	$(CC) $(CFLAGS) $(CPPFLAGS) tests/test_config.c -o $(BUILD_DIR)/test_config $(BUILD_DIR)/libaether_config.a
	$(BUILD_DIR)/test_config

install: all
	install -d $(DESTDIR)$(PREFIX)/lib $(DESTDIR)$(PREFIX)/include/aether_config
	install -m 0644 $(BUILD_DIR)/libaether_config.a $(DESTDIR)$(PREFIX)/lib/
	install -m 0644 include/aether_config/*.h $(DESTDIR)$(PREFIX)/include/aether_config/

uninstall:
	rm -f $(DESTDIR)$(PREFIX)/lib/libaether_config.a
	rm -rf $(DESTDIR)$(PREFIX)/include/aether_config

clean:
	rm -rf $(BUILD_DIR)
