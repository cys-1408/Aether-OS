PREFIX ?= /usr
install:
	install -d $(DESTDIR)$(PREFIX)/libexec/aether/logging
	cp -r *.py $(DESTDIR)$(PREFIX)/libexec/aether/logging/
check:
	python3 -m compileall -q .
