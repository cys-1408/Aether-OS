PREFIX ?= /usr
install:
	install -d $(DESTDIR)$(PREFIX)/libexec/aether/miso/broker
	cp -r *.py $(DESTDIR)$(PREFIX)/libexec/aether/miso/broker/
check:
	python3 -m compileall -q .
