PREFIX ?= /usr
install:
	install -d $(DESTDIR)$(PREFIX)/libexec/aether/trash
	cp -r *.py *.json $(DESTDIR)$(PREFIX)/libexec/aether/trash/
check:
	python3 -m compileall -q .
