"""System tray indicator using AyatanaAppIndicator3 (StatusNotifierItem)."""

import os
import subprocess
import threading
import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GLib

from . import proxyctl
from .profiles import ProfileManager
from .notifier import notify

ICON_DIR = os.path.join(os.path.dirname(__file__), "icons")
ICON_ON = os.path.join(ICON_DIR, "novapm-on.png")
ICON_OFF = os.path.join(ICON_DIR, "novapm-off.png")


class TrayIndicator:
    def __init__(self, app, window):
        self.app = app
        self.window = window
        self.indicator = None
        self.menu = None
        self.toggle_item = None
        self._build()

    def _build(self):
        try:
            gi.require_version("AyatanaAppIndicator3", "0.1")
            from gi.repository import AyatanaAppIndicator3 as AII3
        except (ValueError, ImportError):
            self._install_dependency()
            return

        self.indicator = AII3.Indicator.new(
            "novapm",
            "novapm",
            AII3.IndicatorCategory.APPLICATION_STATUS,
        )
        self.menu = Gtk.Menu()

        self._rebuild_menu()
        self.menu.show_all()
        self.indicator.set_menu(self.menu)
        self.indicator.set_status(AII3.IndicatorStatus.ACTIVE)
        self.indicator.set_icon_full(ICON_OFF, "NovaProxy desactivado")

    def _rebuild_menu(self):
        for child in self.menu.get_children():
            self.menu.remove(child)

        abrir = Gtk.MenuItem(label="Abrir NovaProxy")
        abrir.connect("activate", lambda *a: self._show_window())
        self.menu.append(abrir)

        self.toggle_item = Gtk.MenuItem(label="Activar")
        self.toggle_item.connect("activate", lambda *a: self._toggle())
        self.menu.append(self.toggle_item)

        self.menu.append(Gtk.SeparatorMenuItem())

        pm = ProfileManager()
        current = pm.current()
        names = pm.list()

        perfil_item = Gtk.MenuItem(label=f"Perfil: {current or '—'}")
        perfil_item.set_sensitive(False)
        self.menu.append(perfil_item)

        perfiles_menu = Gtk.Menu()
        perfiles_item = Gtk.MenuItem(label="Perfiles ►")
        if names:
            for name in names:
                label = f"● {name}" if name == current else f"   {name}"
                item = Gtk.MenuItem(label=label)
                item.connect("activate", lambda *a, n=name: self._switch_profile(n))
                perfiles_menu.append(item)
        else:
            empty = Gtk.MenuItem(label="Sin perfiles")
            empty.set_sensitive(False)
            perfiles_menu.append(empty)

        perfiles_menu.append(Gtk.SeparatorMenuItem())
        gestionar = Gtk.MenuItem(label="Gestionar perfiles…")
        gestionar.connect("activate", lambda *a: self._open_profiles())
        perfiles_menu.append(gestionar)

        perfiles_item.set_submenu(perfiles_menu)
        self.menu.append(perfiles_item)

        self.menu.append(Gtk.SeparatorMenuItem())

        config = Gtk.MenuItem(label="Configuración")
        config.connect("activate", lambda *a: self._open_config())
        self.menu.append(config)

        self.menu.append(Gtk.SeparatorMenuItem())

        salir = Gtk.MenuItem(label="Salir")
        salir.connect("activate", lambda *a: self._on_quit())
        self.menu.append(salir)

        self.menu.show_all()

    def _switch_profile(self, name):
        def _run():
            pm = ProfileManager()
            success, output = pm.switch(name)
            if not success:
                GLib.idle_add(lambda: notify("NovaProxy", f"Error al aplicar: {output[:80]}"))
                return
            GLib.idle_add(self._rebuild_menu)
            GLib.idle_add(lambda: self.window._update_ui())

        threading.Thread(target=_run, daemon=True).start()

    def _open_profiles(self):
        from .profiles_window import ProfilesWindow

        def _refresh_all(*args):
            self._rebuild_menu()
            self.window._update_ui()

        pw = ProfilesWindow(self.window.window, on_switch=_refresh_all, on_change=_refresh_all)
        pw.show()

    def _install_dependency(self):
        dialog = Gtk.MessageDialog(
            transient_for=None,
            modal=True,
            message_type=Gtk.MessageType.ERROR,
            buttons=Gtk.ButtonsType.NONE,
            text="Falta dependencia: AyatanaAppIndicator3",
        )
        dialog.format_secondary_text(
            "Proxy GUI necesita la libreria AyatanaAppIndicator3\n"
            "para mostrar el icono en el panel del sistema.\n\n"
            "Desea instalarla ahora?"
        )
        dialog.add_button("Cancelar", Gtk.ResponseType.CANCEL)
        install_btn = dialog.add_button(
            "Instalar", Gtk.ResponseType.OK
        )
        install_btn.get_style_context().add_class("suggested-action")

        response = dialog.run()
        dialog.destroy()

        if response == Gtk.ResponseType.OK:
            env = os.environ.copy()
            askpass = proxyctl.ASKPASS
            if askpass.exists():
                env["SUDO_ASKPASS"] = str(askpass)

            result = subprocess.run(
                [
                    "sudo", "-A", "apt", "install", "-y",
                    "gir1.2-ayatanaappindicator3-0.1",
                    "libayatana-appindicator3-1",
                ],
                capture_output=True, text=True, timeout=120,
                env=env,
            )

            if result.returncode == 0:
                try:
                    gi.require_version("AyatanaAppIndicator3", "0.1")
                    from gi.repository import AyatanaAppIndicator3 as AII3
                    self._build_after_install(AII3)
                    return
                except (ValueError, ImportError):
                    pass

            err = Gtk.MessageDialog(
                transient_for=None,
                modal=True,
                message_type=Gtk.MessageType.ERROR,
                buttons=Gtk.ButtonsType.CLOSE,
                text="No se pudo instalar AyatanaAppIndicator3",
            )
            err.format_secondary_text(
                "Instale manualmente:\n\n"
                "  sudo apt install gir1.2-ayatanaappindicator3-0.1 libayatana-appindicator3-1"
            )
            err.run()
            err.destroy()

    def _build_after_install(self, AII3):
        self.indicator = AII3.Indicator.new(
            "novapm", "novapm",
            AII3.IndicatorCategory.APPLICATION_STATUS,
        )
        self.menu = Gtk.Menu()

        self._rebuild_menu()
        self.menu.show_all()
        self.indicator.set_menu(self.menu)
        self.indicator.set_status(AII3.IndicatorStatus.ACTIVE)
        self.indicator.set_icon_full(ICON_OFF, "NovaProxy desactivado")
        self.window.window.present()

    def _on_quit(self):
        proxyctl.run_proxy("off")
        self.app.quit()

    def _show_window(self):
        self.window.show()
        self.window.window.present()

    def update_status(self, running: bool):
        if self.indicator is None:
            return
        if running:
            self.indicator.set_icon_full(ICON_ON, "NovaProxy activado")
            if self.toggle_item:
                self.toggle_item.set_label("Desactivar")
        else:
            self.indicator.set_icon_full(ICON_OFF, "NovaProxy desactivado")
            if self.toggle_item:
                self.toggle_item.set_label("Activar")

    def _toggle(self):
        running = proxyctl.is_proxy_local_running()

        def _run():
            if running:
                proxyctl.run_proxy("off")
                GLib.idle_add(lambda: notify("NovaProxy", "Proxy desactivado"))
            else:
                success, _ = proxyctl.run_proxy("on")
                if success:
                    GLib.idle_add(lambda: notify("NovaProxy", "Proxy activado"))
            GLib.idle_add(lambda: self.window._update_ui())

        threading.Thread(target=_run, daemon=True).start()

    def _open_config(self):
        self.window._on_open_config()
        self._show_window()
