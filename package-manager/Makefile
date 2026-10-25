PREFIX ?= /usr
install:
	install -d $(DESTDIR)$(PREFIX)/libexec/aether/package-manager
	cp -r core repo integrity cli ui-bridge $(DESTDIR)$(PREFIX)/libexec/aether/package-manager/
	install -Dm755 cli/aether_pm.py $(DESTDIR)$(PREFIX)/libexec/aether/aether-pm
check:
	python3 -m compileall -q core repo integrity cli ui-bridge
