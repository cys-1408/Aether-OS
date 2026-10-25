PREFIX ?= /usr
install:
	install -d $(DESTDIR)$(PREFIX)/libexec/aether/ai
	cp -r runtime firstboot ui $(DESTDIR)$(PREFIX)/libexec/aether/ai/
	install -d $(DESTDIR)$(PREFIX)/share/aether/ai/catalog
	install -m644 catalog/catalog.json catalog/catalog.schema.json catalog/catalog.json.sha256 catalog/sources-policy.yaml catalog/README.md $(DESTDIR)$(PREFIX)/share/aether/ai/catalog/
	install -d $(DESTDIR)$(PREFIX)/share/aether/ai/policies
	install -m644 policies/*.yaml $(DESTDIR)$(PREFIX)/share/aether/ai/policies/
check:
	python3 -m compileall -q runtime firstboot ui
