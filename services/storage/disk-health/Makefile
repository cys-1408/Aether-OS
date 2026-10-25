PREFIX ?= /usr
install:
	install -d $(DESTDIR)$(PREFIX)/libexec/aether/disk-health
	cp -r *.py $(DESTDIR)$(PREFIX)/libexec/aether/disk-health/
check:
	python3 -m compileall -q .
