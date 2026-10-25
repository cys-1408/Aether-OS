PREFIX ?= /usr
install:
	install -d $(DESTDIR)$(PREFIX)/libexec/aether/system/firstboot
	cp -r *.py *.json $(DESTDIR)$(PREFIX)/libexec/aether/system/firstboot/
check:
	python3 -m compileall -q .
