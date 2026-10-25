PREFIX ?= /usr
install:
	install -d $(DESTDIR)$(PREFIX)/libexec/aether/backup
	cp -r *.py *.json $(DESTDIR)$(PREFIX)/libexec/aether/backup/
check:
	python3 -m compileall -q .
