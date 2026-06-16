"""Self-uninstall module. Writes a cleanup script and executes it."""

import os
import sys
import subprocess
import shutil

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GLib


CLEANUP_SCRIPT = """#!/usr/bin/env bash
set -e

APP="novapm"
HOME_DIR="$HOME"
CONFIG_DIR="$HOME_DIR/.config/proxy"
LOCAL_BIN="$HOME_DIR/.local/bin"
SYSTEMD_USER="$HOME_DIR/.config/systemd/user"
PREFIX="/usr/local"

echo "[NovaProxy] Deteniendo servicio systemd..."
systemctl --user stop "$APP-local.service" 2>/dev/null || true
systemctl --user disable "$APP-local.service" 2>/dev/null || true

echo "[NovaProxy] Eliminando scripts locales..."
rm -f "$LOCAL_BIN/$APP" 2>/dev/null || true
rm -f "$LOCAL_BIN/$APP-bash" 2>/dev/null || true
rm -f "$LOCAL_BIN/$APP-local.py" 2>/dev/null || true
rm -f "$LOCAL_BIN/proxy-askpass" 2>/dev/null || true
rm -f "$LOCAL_BIN/proxy-bash" 2>/dev/null || true
rm -f "$LOCAL_BIN/proxy-local.py" 2>/dev/null || true

echo "[NovaProxy] Eliminando configuracion..."
rm -rf "$CONFIG_DIR" 2>/dev/null || true

echo "[NovaProxy] Eliminando servicio systemd..."
rm -f "$SYSTEMD_USER/$APP-local.service" 2>/dev/null || true
systemctl --user daemon-reload 2>/dev/null || true

echo "[NovaProxy] Eliminando .desktop e iconos..."
rm -f "$PREFIX/share/applications/$APP.desktop" 2>/dev/null || true
for dir in 16x16 22x22 24x24 32x32 48x48 64x64 72x72 96x96 128x128 256x256 512x512; do
  rm -f "$PREFIX/share/icons/hicolor/$dir/apps/$APP.png" 2>/dev/null || true
  rm -f "$PREFIX/share/icons/hicolor/$dir/apps/$APP-on.png" 2>/dev/null || true
  rm -f "$PREFIX/share/icons/hicolor/$dir/apps/$APP-off.png" 2>/dev/null || true
done
rm -f "$PREFIX/share/icons/hicolor/scalable/apps/$APP.svg" 2>/dev/null || true
rm -f "$PREFIX/share/icons/hicolor/scalable/apps/$APP-on.svg" 2>/dev/null || true
rm -f "$PREFIX/share/icons/hicolor/scalable/apps/$APP-off.svg" 2>/dev/null || true
gtk-update-icon-cache -f /usr/share/icons/hicolor 2>/dev/null || true

echo "[NovaProxy] Eliminando APT source list..."
rm -f /etc/apt/sources.list.d/$APP.list 2>/dev/null || true

echo "[NovaProxy] Desinstalando paquete pipx..."
pipx uninstall "$APP" 2>/dev/null || true

echo ""
echo "[OK] NovaProxy Manager desinstalado correctamente."
"""


def run_uninstall():
    """Write cleanup script to /tmp and execute it with sudo."""
    dialog = Gtk.MessageDialog(
        parent=None,
        flags=Gtk.DialogFlags.DESTROY_WITH_PARENT,
        message_type=Gtk.MessageType.WARNING,
        buttons=Gtk.ButtonsType.YES_NO,
        text="Desinstalar NovaProxy Manager",
    )
    dialog.format_secondary_text(
        "Se eliminarán todos los archivos del programa:\n"
        "• Paquete pipx\n"
        "• Scripts en ~/.local/bin/\n"
        "• Configuración en ~/.config/proxy/\n"
        "• Servicio systemd\n"
        "• Archivo .desktop e iconos\n"
        "• Lista de APT source\n\n"
        "¿Confirmás la desinstalación?"
    )
    response = dialog.run()
    dialog.destroy()

    if response != Gtk.ResponseType.YES:
        return

    script_path = "/tmp/novapm-cleanup.sh"
    with open(script_path, "w") as f:
        f.write(CLEANUP_SCRIPT)
    os.chmod(script_path, 0o755)

    askpass = os.path.expanduser("~/.local/bin/proxy-askpass")
    if os.path.exists(askpass):
        env = os.environ.copy()
        env.setdefault("DISPLAY", ":0")
        env.setdefault("XAUTHORITY", os.path.expanduser("~/.Xauthority"))
        env["SUDO_ASKPASS"] = askpass
    else:
        env = os.environ.copy()

    try:
        subprocess.run(["sudo", "-A", "-k", "/bin/bash", script_path],
                       check=True, env=env)
    except subprocess.CalledProcessError:
        # fallback: run directly (may fail due to permissions on some steps)
        subprocess.run(["/bin/bash", script_path], check=False)

    # If we're still alive, the pipx uninstall probably failed; force pipx removal
    subprocess.run(["pipx", "uninstall", "novapm"], capture_output=True)

    Gtk.main_quit()
    sys.exit(0)
