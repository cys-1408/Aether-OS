PREFIX ?= /usr
install:
	install -d $(DESTDIR)$(PREFIX)/libexec/aether/audio-service
	cp -r *.py $(DESTDIR)$(PREFIX)/libexec/aether/audio-service/
check:
	python3 -m compileall -q .
