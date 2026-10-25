PREFIX ?= /usr
install:
	install -d $(DESTDIR)$(PREFIX)/libexec/aether/authentication
	cp -r *.py $(DESTDIR)$(PREFIX)/libexec/aether/authentication/
check:
	python3 -m compileall -q .
