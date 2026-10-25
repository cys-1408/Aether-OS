PREFIX ?= /usr
install:
	install -d $(DESTDIR)$(PREFIX)/libexec/aether/desktop
	cp -r shell compositor window-manager panels desktop-icons launcher windows theme miso-view focus-mode dialogs notifications accessibility session settings-integration $(DESTDIR)$(PREFIX)/libexec/aether/desktop/
	install -Dm644 assets/miso/miso.svg $(DESTDIR)$(PREFIX)/share/aether/desktop/assets/miso/miso.svg
	cp -r assets/miso $(DESTDIR)$(PREFIX)/share/aether/desktop/assets/
	mkdir -p $(DESTDIR)$(PREFIX)/bin
	printf '#!/bin/sh\nexec python3 $(PREFIX)/libexec/aether/desktop/shell/app_main.py "$$@"\n' > $(DESTDIR)$(PREFIX)/bin/aether-shell
	chmod 755 $(DESTDIR)$(PREFIX)/bin/aether-shell
	printf '#!/bin/sh\nexec python3 $(PREFIX)/libexec/aether/desktop/shell/aetherctl.py "$$@"\n' > $(DESTDIR)$(PREFIX)/bin/aetherctl
	chmod 755 $(DESTDIR)$(PREFIX)/bin/aetherctl
check:
	python3 -m compileall -q .
