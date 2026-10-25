PREFIX ?= /usr
install:
	install -d $(DESTDIR)$(PREFIX)/libexec/aether/power-manager
	cp -r *.py $(DESTDIR)$(PREFIX)/libexec/aether/power-manager/
check:
	python3 -m compileall -q .
