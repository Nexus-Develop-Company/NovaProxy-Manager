.PHONY: install uninstall run deb clean

PREFIX ?= /usr/local
APP = novapm
VERSION = 1.0.0

install:
	sudo apt install -y gir1.2-ayatanaappindicator3-0.1 libayatana-appindicator3-1 2>/dev/null; \
	pipx install --system-site-packages .
	@echo ""
	@echo "Instalado. Ejecuta:  novapm"

install-system:
	pip install .
	install -Dm644 data/novapm.desktop $(DESTDIR)$(PREFIX)/share/applications/novapm.desktop
	# Install app icons to hicolor theme (PNG for all standard sizes)
	for dir in $$(ls data/icons/hicolor); do \
	  install -Dm644 data/icons/hicolor/$$dir/apps/novapm.png \
	    $(DESTDIR)$(PREFIX)/share/icons/hicolor/$$dir/apps/novapm.png; \
	done
	install -Dm644 src/proxy_gui/icons/novapm-on.png \
	  $(DESTDIR)$(PREFIX)/share/icons/hicolor/256x256/apps/novapm-on.png
	install -Dm644 src/proxy_gui/icons/novapm-off.png \
	  $(DESTDIR)$(PREFIX)/share/icons/hicolor/256x256/apps/novapm-off.png
	# Install SVG to scalable directory
	install -Dm644 src/proxy_gui/icons/novapm.svg \
	  $(DESTDIR)$(PREFIX)/share/icons/hicolor/scalable/apps/novapm.svg
	install -Dm644 src/proxy_gui/icons/novapm-on.svg \
	  $(DESTDIR)$(PREFIX)/share/icons/hicolor/scalable/apps/novapm-on.svg
	install -Dm644 src/proxy_gui/icons/novapm-off.svg \
	  $(DESTDIR)$(PREFIX)/share/icons/hicolor/scalable/apps/novapm-off.svg
	gtk-update-icon-cache -f /usr/share/icons/hicolor 2>/dev/null || true

uninstall:
	pip uninstall -y $(APP)
	rm -f $(DESTDIR)$(PREFIX)/share/applications/novapm.desktop
	# Remove all hicolor icon sizes
	for dir in 16x16 22x22 24x24 32x32 48x48 64x64 72x72 96x96 128x128 256x256 512x512; do \
	  rm -f $(DESTDIR)$(PREFIX)/share/icons/hicolor/$$dir/apps/novapm.png; \
	  rm -f $(DESTDIR)$(PREFIX)/share/icons/hicolor/$$dir/apps/novapm-on.png; \
	  rm -f $(DESTDIR)$(PREFIX)/share/icons/hicolor/$$dir/apps/novapm-off.png; \
	done
	rm -f $(DESTDIR)$(PREFIX)/share/icons/hicolor/scalable/apps/novapm.svg
	rm -f $(DESTDIR)$(PREFIX)/share/icons/hicolor/scalable/apps/novapm-on.svg
	rm -f $(DESTDIR)$(PREFIX)/share/icons/hicolor/scalable/apps/novapm-off.svg

run:
	python3 -m proxy_gui

deb:
	dpkg-buildpackage -us -uc -b
	mkdir -p dist
	mv ../$(APP)_$(VERSION)-1_all.deb dist/ 2>/dev/null || true

clean:
	rm -rf build/ dist/ *.egg-info/ __pycache__/ src/*/__pycache__/
	rm -f ../*.deb ../*.ddeb ../*.changes ../*.buildinfo 2>/dev/null || true
