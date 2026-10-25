PREFIX ?= /usr
install:
	install -d $(DESTDIR)$(PREFIX)/libexec/aether/session
	cp -r *.py *.json $(DESTDIR)$(PREFIX)/libexec/aether/session/
check:
	python3 -m compileall -q .
