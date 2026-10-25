PREFIX ?= /usr
install:
	install -d $(DESTDIR)$(PREFIX)/libexec/aether/hardware-probe
	cp -r *.py *.json $(DESTDIR)$(PREFIX)/libexec/aether/hardware-probe/
check:
	python3 -m compileall -q .
