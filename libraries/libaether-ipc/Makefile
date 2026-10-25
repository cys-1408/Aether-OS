PREFIX ?= /usr
DESTDIR ?=
CC ?= cc
CFLAGS ?= -std=c11 -Wall -Wextra -O2

all:
	$(CC) $(CFLAGS) -Iinclude -c src/ipc.c -o ipc.o
	ar rcs libaether-ipc.a ipc.o

install: all
	install -Dm644 libaether-ipc.a $(DESTDIR)$(PREFIX)/lib/libaether-ipc.a
	for h in include/aether_ipc/*.h; do install -Dm644 $$h $(DESTDIR)$(PREFIX)/include/aether_ipc/`basename $$h`; done

clean:
	rm -f *.o libaether-ipc.a
