PREFIX ?= /usr
DESTDIR ?=
CC ?= cc
CFLAGS ?= -std=c11 -D_GNU_SOURCE -Wall -Wextra -O2

all:
	$(CC) $(CFLAGS) -Iinclude -I../libaether-core/include -c src/file_identity.c -o file_identity.o
	$(CC) $(CFLAGS) -Iinclude -I../libaether-core/include -c src/file_ops.c -o file_ops.o
	$(CC) $(CFLAGS) -Iinclude -I../libaether-core/include -c src/permission_check.c -o permission_check.o
	ar rcs libaether-files.a file_identity.o file_ops.o permission_check.o

install: all
	install -Dm644 libaether-files.a $(DESTDIR)$(PREFIX)/lib/libaether-files.a
	for h in include/aether_files/*.h; do install -Dm644 $$h $(DESTDIR)$(PREFIX)/include/aether_files/`basename $$h`; done

clean:
	rm -f *.o libaether-files.a
