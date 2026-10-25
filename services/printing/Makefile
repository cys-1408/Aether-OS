PREFIX ?= /usr
install:
	install -d $(DESTDIR)$(PREFIX)/libexec/aether/printing
	cp -r *.py $(DESTDIR)$(PREFIX)/libexec/aether/printing/
check:
	python3 -m compileall -q .
