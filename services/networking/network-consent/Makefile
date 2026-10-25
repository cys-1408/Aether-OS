PREFIX ?= /usr
install:
	install -d $(DESTDIR)$(PREFIX)/libexec/aether/network-consent
	cp -r *.py $(DESTDIR)$(PREFIX)/libexec/aether/network-consent/
check:
	python3 -m compileall -q .
