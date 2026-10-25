PREFIX ?= /usr
install:
	install -d $(DESTDIR)$(PREFIX)/libexec/aether/apps/screenshot
	cp -r *.py $(DESTDIR)$(PREFIX)/libexec/aether/apps/screenshot/
	install -d $(DESTDIR)$(PREFIX)/share/applications $(DESTDIR)$(PREFIX)/share/icons/hicolor/scalable/apps
	install -m644 data/*.desktop $(DESTDIR)$(PREFIX)/share/applications/
	install -m644 data/*.svg $(DESTDIR)$(PREFIX)/share/icons/hicolor/scalable/apps/
	mkdir -p $(DESTDIR)$(PREFIX)/bin
	printf '#!/bin/sh\nexec python3 $(PREFIX)/libexec/aether/apps/screenshot/main.py "$$@"\n' > $(DESTDIR)$(PREFIX)/bin/aether-screenshot
	chmod 755 $(DESTDIR)$(PREFIX)/bin/aether-screenshot
check:
	python3 -m compileall -q .
