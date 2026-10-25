PREFIX ?= /usr
install:
	install -d $(DESTDIR)$(PREFIX)/libexec/aether/clock-service
	cp -r *.py $(DESTDIR)$(PREFIX)/libexec/aether/clock-service/
check:
	python3 -m compileall -q .
