PREFIX ?= /usr
install:
	mkdir -p $(DESTDIR)$(PREFIX)/libexec/aether
	cp -r . $(DESTDIR)$(PREFIX)/libexec/aether/common

check:
	python3 -m compileall -q .
