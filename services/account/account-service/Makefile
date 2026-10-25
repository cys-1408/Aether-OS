PREFIX ?= /usr
install:
	install -d $(DESTDIR)$(PREFIX)/libexec/aether/account-service
	cp -r *.py $(DESTDIR)$(PREFIX)/libexec/aether/account-service/
check:
	python3 -m compileall -q .
