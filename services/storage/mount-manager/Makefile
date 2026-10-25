PREFIX ?= /usr
install:
	install -d $(DESTDIR)$(PREFIX)/libexec/aether/mount-manager
	cp -r *.py $(DESTDIR)$(PREFIX)/libexec/aether/mount-manager/
check:
	python3 -m compileall -q .
