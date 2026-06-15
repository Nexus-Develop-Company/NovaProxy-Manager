"""NovaProxy Manager - Entry point."""

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gio

from . import proxyctl
from .main_window import MainWindow
from .tray import TrayIndicator


class NovaProxyApp(Gtk.Application):
    def __init__(self):
        super().__init__(
            application_id="com.novapm.manager",
            flags=Gio.ApplicationFlags.FLAGS_NONE,
        )
        self.win = None
        self.tray = None

    def do_startup(self):
        Gtk.Application.do_startup(self)
        proxyctl.ensure_files()

    def do_activate(self):
        if self.win is None:
            self.win = MainWindow()
            self.win.window.set_application(self)
            self.tray = TrayIndicator(self, self.win)
            self.win.set_tray(self.tray)
        if self.win.window.get_visible():
            self.win.window.present()
        else:
            self.tray._show_window()

    def do_shutdown(self):
        running = proxyctl.is_proxy_local_running()
        if running:
            proxyctl.run_proxy("off")
            from .notifier import notify
            notify("NovaProxy", "Proxy desactivado al cerrar la app")
        Gtk.Application.do_shutdown(self)


def main():
    app = NovaProxyApp()
    app.run()


if __name__ == "__main__":
    main()
