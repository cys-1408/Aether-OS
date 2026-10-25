PREFIX ?= /usr
install:
	install -d $(DESTDIR)$(PREFIX)/libexec/aether/clipboard
	cp -r *.py $(DESTDIR)$(PREFIX)/libexec/aether/clipboard/
check:
	python3 -m compileall -q .
