PREFIX ?= /usr
install:
	install -d $(DESTDIR)$(PREFIX)/libexec/aether/firewall
	cp -r *.py $(DESTDIR)$(PREFIX)/libexec/aether/firewall/
	install -Dm644 default_rules.nft $(DESTDIR)/etc/aether/firewall/default.nft
check:
	python3 -m compileall -q .
