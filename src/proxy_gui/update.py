"""Auto-update module — check GitHub Releases and install new version."""

import json
import os
import re
import subprocess
import sys
import tempfile
import urllib.request
import urllib.error

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GLib

from . import __version__
from .proxyctl import parse_config

REPO = "Nexus-Develop-Company/NovaProxy-Manager"
API_URL = f"https://api.github.com/repos/{REPO}/releases/latest"
TIMEOUT = 15


def _parse_tag(tag: str) -> tuple:
    match = re.match(r"v?(\d+)\.(\d+)\.(\d+)", tag)
    if match:
        return tuple(int(g) for g in match.groups())
    return (0, 0, 0)


def _make_opener():
    """Create urllib opener with corporate proxy if configured."""
    cfg = parse_config()
    proxy_url = cfg.get("http_proxy") or os.environ.get("http_proxy")
    if proxy_url:
        proxy_handler = urllib.request.ProxyHandler({"http": proxy_url, "https": proxy_url})
        return urllib.request.build_opener(proxy_handler)
    return urllib.request.build_opener()


def _latest_release() -> dict | None:
    try:
        req = urllib.request.Request(API_URL, headers={"Accept": "application/json", "User-Agent": "novapm"})
        opener = _make_opener()
        with opener.open(req, timeout=TIMEOUT) as r:
            return json.loads(r.read().decode())
    except (urllib.error.URLError, json.JSONDecodeError, OSError):
        return None


def check_update() -> tuple[str, str] | None:
    data = _latest_release()
    if not data:
        return None
    tag = data.get("tag_name", "")
    if not tag:
        return None
    latest = _parse_tag(tag)
    current = _parse_tag(__version__)
    if latest <= current:
        return None
    assets = data.get("assets", [])
    deb_url = None
    for a in assets:
        if a.get("name", "").endswith(".deb"):
            deb_url = a.get("browser_download_url")
            break
    if not deb_url:
        deb_url = data.get("html_url", "")
    return (tag.lstrip("v"), deb_url)


def run_update():
    result = check_update()
    if result is None:
        dialog = Gtk.MessageDialog(
            parent=None,
            flags=Gtk.DialogFlags.DESTROY_WITH_PARENT,
            message_type=Gtk.MessageType.INFO,
            buttons=Gtk.ButtonsType.OK,
            text="No hay actualizaciones disponibles",
        )
        dialog.format_secondary_text(f"Tenés la versión {__version__}, que es la más reciente.")
        dialog.run()
        dialog.destroy()
        return

    latest_ver, deb_url = result

    dialog = Gtk.MessageDialog(
        parent=None,
        flags=Gtk.DialogFlags.DESTROY_WITH_PARENT,
        message_type=Gtk.MessageType.QUESTION,
        buttons=Gtk.ButtonsType.YES_NO,
        text=f"Nueva versión disponible: {latest_ver}",
    )
    dialog.format_secondary_text(
        f"Actualmente tenés la versión {__version__}.\n"
        f"¿Descargar e instalar la versión {latest_ver}?"
    )
    response = dialog.run()
    dialog.destroy()

    if response != Gtk.ResponseType.YES:
        return

    progress = Gtk.MessageDialog(
        parent=None,
        flags=Gtk.DialogFlags.DESTROY_WITH_PARENT,
        message_type=Gtk.MessageType.INFO,
        buttons=Gtk.ButtonsType.NONE,
        text="Descargando actualización...",
    )
    progress.show_all()

    try:
        deb_path = os.path.join(tempfile.gettempdir(), f"novapm_{latest_ver}.deb")
        req = urllib.request.Request(deb_url, headers={"User-Agent": "novapm"})
        opener = _make_opener()
        with opener.open(req, timeout=60) as r:
            with open(deb_path, "wb") as f:
                f.write(r.read())

        progress.destroy()

        askpass = os.path.expanduser("~/.local/bin/proxy-askpass")
        env = os.environ.copy()
        env.setdefault("DISPLAY", ":0")
        env.setdefault("XAUTHORITY", os.path.expanduser("~/.Xauthority"))
        if os.path.exists(askpass):
            env["SUDO_ASKPASS"] = askpass

        result = subprocess.run(
            ["sudo", "-A", "apt", "install", "--reinstall", "-y", deb_path],
            capture_output=True, text=True, timeout=120, env=env,
        )

        if result.returncode == 0:
            Gtk.MessageDialog(
                parent=None,
                flags=Gtk.DialogFlags.DESTROY_WITH_PARENT,
                message_type=Gtk.MessageType.INFO,
                buttons=Gtk.ButtonsType.OK,
                text="Actualización completada",
            ).run()
        else:
            Gtk.MessageDialog(
                parent=None,
                flags=Gtk.DialogFlags.DESTROY_WITH_PARENT,
                message_type=Gtk.MessageType.ERROR,
                buttons=Gtk.ButtonsType.OK,
                text="Error al instalar",
            ).run()
    except Exception as e:
        if progress.get_property("visible"):
            progress.destroy()
        Gtk.MessageDialog(
            parent=None,
            flags=Gtk.DialogFlags.DESTROY_WITH_PARENT,
            message_type=Gtk.MessageType.ERROR,
            buttons=Gtk.ButtonsType.OK,
            text="Error en la actualización",
        ).run()

    return
