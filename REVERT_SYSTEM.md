# REVERT SYSTEM — NovaProxy Manager

Este documento lista **todo lo que se modificó en el sistema** fuera del proyecto
durante la instalación/desarrollo. Usalo para dejar el sistema "virgen" para
probar una instalación desde cero.

---

## 1. Paquetes apt instalados

```bash
sudo apt remove --purge gh debhelper dh-python dpkg-dev
```

## 2. Pipx — novapm

```bash
pipx uninstall novapm
```

## 3. Scripts en ~/.local/bin/

```bash
rm -f ~/.local/bin/novapm ~/.local/bin/novapm-bash
rm -f ~/.local/bin/novapm-local.py ~/.local/bin/proxy-askpass
rm -f ~/.local/bin/proxy-bash ~/.local/bin/proxy-local.py
```

## 4. Configuración

```bash
rm -rf ~/.config/proxy/
```

## 5. Servicio systemd usuario

```bash
systemctl --user stop novapm-local.service 2>/dev/null
systemctl --user disable novapm-local.service 2>/dev/null
rm -f ~/.config/systemd/user/novapm-local.service
systemctl --user daemon-reload
```

## 6. Desktop file

```bash
sudo rm -f /usr/local/share/applications/novapm.desktop
```

## 7. Iconos hicolor

```bash
for dir in 16x16 22x22 24x24 32x32 48x48 64x64 72x72 96x96 128x128 256x256 512x512; do
  sudo rm -f /usr/local/share/icons/hicolor/$dir/apps/novapm.png
  sudo rm -f /usr/local/share/icons/hicolor/$dir/apps/novapm-on.png
  sudo rm -f /usr/local/share/icons/hicolor/$dir/apps/novapm-off.png
done
sudo rm -f /usr/local/share/icons/hicolor/scalable/apps/novapm.svg
sudo rm -f /usr/local/share/icons/hicolor/scalable/apps/novapm-on.svg
sudo rm -f /usr/local/share/icons/hicolor/scalable/apps/novapm-off.svg
sudo gtk-update-icon-cache -f /usr/share/icons/hicolor
```

## 8. GPG key (firma APT repo)

```bash
gpg --delete-secret-key "Nexus Develop Company" 2>/dev/null
gpg --delete-key "Nexus Develop Company" 2>/dev/null
```

## 9. APT source list (si se agregó)

```bash
sudo rm -f /etc/apt/sources.list.d/novapm.list
```

## 10. GitHub Secrets (web)

Ir a `Settings → Secrets and variables → Actions` y borrar:
- `GPG_PRIVATE_KEY`
- `GPG_PASSPHRASE`

---

## Resumen rápido (un solo bloque)

```bash
pipx uninstall novapm 2>/dev/null
rm -f ~/.local/bin/novapm ~/.local/bin/novapm-bash ~/.local/bin/novapm-local.py ~/.local/bin/proxy-askpass ~/.local/bin/proxy-bash ~/.local/bin/proxy-local.py
rm -rf ~/.config/proxy/
systemctl --user stop novapm-local.service 2>/dev/null; systemctl --user disable novapm-local.service 2>/dev/null
rm -f ~/.config/systemd/user/novapm-local.service; systemctl --user daemon-reload
sudo rm -f /usr/local/share/applications/novapm.desktop
for dir in 16x16 22x22 24x24 32x32 48x48 64x64 72x72 96x96 128x128 256x256 512x512; do sudo rm -f /usr/local/share/icons/hicolor/$dir/apps/novapm*.png; done
sudo rm -f /usr/local/share/icons/hicolor/scalable/apps/novapm*.svg
sudo gtk-update-icon-cache -f /usr/share/icons/hicolor 2>/dev/null
gpg --delete-secret-key "Nexus Develop Company" 2>/dev/null; gpg --delete-key "Nexus Develop Company" 2>/dev/null
sudo rm -f /etc/apt/sources.list.d/novapm.list
```
