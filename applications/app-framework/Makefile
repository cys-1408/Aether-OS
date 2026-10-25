PREFIX ?= /usr
install:
	install -d $(DESTDIR)$(PREFIX)/libexec/aether/app-framework
	cp -r *.py *.json $(DESTDIR)$(PREFIX)/libexec/aether/app-framework/
check:
	python3 -m compileall -q .
