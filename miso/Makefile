PREFIX ?= /usr
install:
	install -d $(DESTDIR)$(PREFIX)/libexec/aether/miso
	cp -r agent runtime-client capability-os broker policy-engine capabilities ledger workspaces presence safety ui $(DESTDIR)$(PREFIX)/libexec/aether/miso/
	install -d $(DESTDIR)$(PREFIX)/etc/aether/policy
	install -m644 policy-engine/*.yaml $(DESTDIR)$(PREFIX)/etc/aether/policy/ 2>/dev/null || true
check:
	python3 -m compileall -q agent runtime-client capability-os broker policy-engine capabilities ledger workspaces presence safety ui
