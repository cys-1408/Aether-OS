PREFIX ?= /usr
install:
	install -d $(DESTDIR)$(PREFIX)/libexec/aether/miso/agent
	cp -r *.py *.json $(DESTDIR)$(PREFIX)/libexec/aether/miso/agent/
check:
	python3 -m compileall -q .
