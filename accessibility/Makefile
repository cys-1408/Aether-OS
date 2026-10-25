PREFIX ?= /usr
install:
	install -d $(DESTDIR)$(PREFIX)/libexec/aether/accessibility
	cp -r *.py *.yaml $(DESTDIR)$(PREFIX)/libexec/aether/accessibility/
check:
	python3 -m compileall -q .
