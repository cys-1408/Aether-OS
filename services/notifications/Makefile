PREFIX ?= /usr
install:
	install -d $(DESTDIR)$(PREFIX)/libexec/aether/notifications
	cp -r *.py *.json $(DESTDIR)$(PREFIX)/libexec/aether/notifications/
check:
	python3 -m compileall -q .
