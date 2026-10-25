PREFIX ?= /usr
install:
	install -d $(DESTDIR)$(PREFIX)/libexec/aether/miso/ledger
	cp -r *.py *.sql *.json $(DESTDIR)$(PREFIX)/libexec/aether/miso/ledger/
check:
	python3 -m compileall -q .
