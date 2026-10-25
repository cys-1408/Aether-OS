PREFIX ?= /usr
install:
	install -d $(DESTDIR)$(PREFIX)/libexec/aether/device-events
	cp -r *.py $(DESTDIR)$(PREFIX)/libexec/aether/device-events/
check:
	python3 -m compileall -q .
