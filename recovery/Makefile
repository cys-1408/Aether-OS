PREFIX ?= /usr
install:
	install -d $(DESTDIR)$(PREFIX)/libexec/aether/recovery
	cp -r recovery-entry diagnostics repair rollback backup ui $(DESTDIR)$(PREFIX)/libexec/aether/recovery/
	mkdir -p $(DESTDIR)$(PREFIX)/bin
	printf '#!/bin/sh\nexec python3 $(PREFIX)/libexec/aether/recovery/recovery-entry/recovery_main.py "$$@"\n' > $(DESTDIR)$(PREFIX)/bin/aether-recovery
	chmod 755 $(DESTDIR)$(PREFIX)/bin/aether-recovery
check:
	python3 -m compileall -q recovery-entry diagnostics repair rollback backup ui
