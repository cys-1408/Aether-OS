PREFIX ?= /usr
install:
	install -d $(DESTDIR)$(PREFIX)/libexec/aether/voice-input
	cp -r *.py $(DESTDIR)$(PREFIX)/libexec/aether/voice-input/
check:
	python3 -m compileall -q .
