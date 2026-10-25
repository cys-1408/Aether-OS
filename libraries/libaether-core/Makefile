# Install the C library + the Python package.
PREFIX ?= /usr
DESTDIR ?=
CC ?= cc
CFLAGS ?= -std=c11 -D_GNU_SOURCE -Wall -Wextra -O2

all:
	$(CC) $(CFLAGS) -Iinclude -c src/result.c -o result.o
	$(CC) $(CFLAGS) -Iinclude -c src/error.c -o error.o
	$(CC) $(CFLAGS) -Iinclude -c src/cancellation.c -o cancellation.o
	$(CC) $(CFLAGS) -Iinclude -c src/resource_limits.c -o resource_limits.o
	ar rcs libaether-core.a result.o error.o cancellation.o resource_limits.o

check: all
	$(CC) $(CFLAGS) -Iinclude tests/test_core.c libaether-core.a -o /tmp/aether-test-core && /tmp/aether-test-core && echo "C core tests passed"

install: all
	install -Dm644 libaether-core.a $(DESTDIR)$(PREFIX)/lib/libaether-core.a
	for h in include/aether_core/*.h; do install -Dm644 $$h $(DESTDIR)$(PREFIX)/include/aether_core/`basename $$h`; done
	mkdir -p $(DESTDIR)$(PREFIX)/lib/aether/python
	cp -r python/aether_core $(DESTDIR)$(PREFIX)/lib/aether/python/

clean:
	rm -f *.o libaether-core.a
