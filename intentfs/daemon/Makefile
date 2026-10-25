PREFIX ?= /usr
install:
	install -d $(DESTDIR)$(PREFIX)/libexec/aether/intentfs/daemon
	cp -r *.py $(DESTDIR)$(PREFIX)/libexec/aether/intentfs/daemon/
check:
	python3 -m compileall -q .
