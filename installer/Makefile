PREFIX ?= /usr
install:
	install -d $(DESTDIR)$(PREFIX)/libexec/aether/installer
	cp -r app screens storage install logging recovery schemas $(DESTDIR)$(PREFIX)/libexec/aether/installer/
check:
	python3 -m compileall -q app screens storage install logging recovery
