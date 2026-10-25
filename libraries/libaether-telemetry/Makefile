# libaether-telemetry — Makefile
DESTDIR   ?=
PREFIX    ?= /usr
BUILD_DIR = build

SOURCES = src/system_metrics.c src/metrics_redaction.c
OBJECTS = $(patsubst src/%.c,$(BUILD_DIR)/%.o,$(SOURCES))

CFLAGS  ?= -std=c11 -Wall -Wextra -O2
CPPFLAGS += -Iinclude -Isrc -D_GNU_SOURCE -D_POSIX_C_SOURCE=200809L -D_DEFAULT_SOURCE

.PHONY: all test install uninstall clean

all: $(BUILD_DIR)/libaether_telemetry.a

$(BUILD_DIR)/libaether_telemetry.a: $(OBJECTS)
	ar rcs $@ $^

$(BUILD_DIR)/%.o: src/%.c
	$(CC) $(CFLAGS) $(CPPFLAGS) -c $< -o $@

test: $(BUILD_DIR)/libaether_telemetry.a
	$(CC) $(CFLAGS) $(CPPFLAGS) tests/test_telemetry.c -o $(BUILD_DIR)/test_telemetry $(BUILD_DIR)/libaether_telemetry.a
	$(BUILD_DIR)/test_telemetry

install: all
	install -d $(DESTDIR)$(PREFIX)/lib $(DESTDIR)$(PREFIX)/include/aether_telemetry
	install -m 0644 $(BUILD_DIR)/libaether_telemetry.a $(DESTDIR)$(PREFIX)/lib/
	install -m 0644 include/aether_telemetry/*.h $(DESTDIR)$(PREFIX)/include/aether_telemetry/

uninstall:
	rm -f $(DESTDIR)$(PREFIX)/lib/libaether_telemetry.a
	rm -rf $(DESTDIR)$(PREFIX)/include/aether_telemetry

clean:
	rm -rf $(BUILD_DIR)
