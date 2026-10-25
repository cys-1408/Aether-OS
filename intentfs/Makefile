PREFIX ?= /usr
install:
	install -d $(DESTDIR)$(PREFIX)/libexec/aether/intentfs
	cp -r daemon watcher pipeline extraction concepts index search privacy api ui $(DESTDIR)$(PREFIX)/libexec/aether/intentfs/
check:
	python3 -m compileall -q daemon watcher pipeline extraction concepts index search privacy api ui
