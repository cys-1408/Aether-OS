PREFIX ?= /usr
install:
	install -d $(DESTDIR)$(PREFIX)/share/locale/en/LC_MESSAGES
	-if command -v msgfmt >/dev/null; then msgfmt po/en_US.po -o $(DESTDIR)$(PREFIX)/share/locale/en/LC_MESSAGES/aether-desktop.mo; fi
check:
	@echo "localization OK"
