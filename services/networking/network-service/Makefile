PREFIX ?= /usr
install:
	install -d $(DESTDIR)$(PREFIX)/libexec/aether/network-service
	cp -r *.py *.json $(DESTDIR)$(PREFIX)/libexec/aether/network-service/
check:
	python3 -m compileall -q .
