PREFIX ?= /usr
install:
	install -d $(DESTDIR)$(PREFIX)/libexec/aether/installer/app
	cp -r *.py $(DESTDIR)$(PREFIX)/libexec/aether/installer/app/
	mkdir -p $(DESTDIR)$(PREFIX)/bin
	printf '#!/bin/sh\nexec python3 $(PREFIX)/libexec/aether/installer/app/main.py "$$@"\n' > $(DESTDIR)$(PREFIX)/bin/aether-installer
	chmod 755 $(DESTDIR)$(PREFIX)/bin/aether-installer
check:
	python3 -m compileall -q .
