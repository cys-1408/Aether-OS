PREFIX ?= /usr
install:
	install -d $(DESTDIR)$(PREFIX)/libexec/aether/scheduler
	cp -r *.py *.json $(DESTDIR)$(PREFIX)/libexec/aether/scheduler/
check:
	python3 -m compileall -q .
