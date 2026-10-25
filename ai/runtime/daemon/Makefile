PREFIX ?= /usr
install:
	install -d $(DESTDIR)$(PREFIX)/libexec/aether/ai/runtime/daemon
	cp -r *.py $(DESTDIR)$(PREFIX)/libexec/aether/ai/runtime/daemon/
check:
	python3 -m compileall -q .
