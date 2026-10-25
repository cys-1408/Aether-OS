PREFIX ?= /usr
install:
	install -d $(DESTDIR)$(PREFIX)/libexec/aether/miso/workspaces
	cp -r *.py *.json $(DESTDIR)$(PREFIX)/libexec/aether/miso/workspaces/
check:
	python3 -m compileall -q .
