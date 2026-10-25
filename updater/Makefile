PREFIX ?= /usr
install:
	install -d $(DESTDIR)$(PREFIX)/libexec/aether/updater
	cp -r *.py $(DESTDIR)$(PREFIX)/libexec/aether/updater/
	mkdir -p $(DESTDIR)$(PREFIX)/bin
	printf '#!/bin/sh\nexec python3 $(PREFIX)/libexec/aether/updater/cli/aether_update.py "$$@"\n' > $(DESTDIR)$(PREFIX)/bin/aether-update
	chmod 755 $(DESTDIR)$(PREFIX)/bin/aether-update
check:
	python3 -m compileall -q .
