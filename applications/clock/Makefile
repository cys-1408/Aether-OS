PREFIX ?= /usr
install:
	install -d $(DESTDIR)$(PREFIX)/libexec/aether/apps/clock
	cp -r *.py $(DESTDIR)$(PREFIX)/libexec/aether/apps/clock/
	install -d $(DESTDIR)$(PREFIX)/share/applications $(DESTDIR)$(PREFIX)/share/icons/hicolor/scalable/apps
	install -m644 data/*.desktop $(DESTDIR)$(PREFIX)/share/applications/
	install -m644 data/*.svg $(DESTDIR)$(PREFIX)/share/icons/hicolor/scalable/apps/
	mkdir -p $(DESTDIR)$(PREFIX)/bin
	printf '#!/bin/sh\nexec python3 $(PREFIX)/libexec/aether/apps/clock/main.py "$$@"\n' > $(DESTDIR)$(PREFIX)/bin/aether-clock
	chmod 755 $(DESTDIR)$(PREFIX)/bin/aether-clock
check:
	python3 -m compileall -q .
