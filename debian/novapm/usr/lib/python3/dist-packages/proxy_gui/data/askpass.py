#!/usr/bin/env python3
"""GTK askpass dialog for sudo -A. Prints password to stdout."""

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk
import sys
import os


ASKPASS_CSS = b"""
window {
    background-color: #1e1e2e;
}
label {
    color: #cdd6f4;
}
entry {
    background-color: #313244;
    color: #cdd6f4;
    border: 1px solid #45475a;
    border-radius: 6px;
    padding: 8px 12px;
    font-size: 13px;
}
button {
    border-radius: 6px;
    padding: 8px 20px;
    font-size: 13px;
}
button.suggested-action {
    background: linear-gradient(135deg, #2ecc71, #27ae60);
    color: #fff;
    border: none;
    font-weight: bold;
}
button.suggested-action:hover {
    background: linear-gradient(135deg, #27ae60, #1e8449);
}
"""


class AskPassDialog:
    def __init__(self):
        self.password = ""
        self._build()

    def _build(self):
        css = Gtk.CssProvider()
        css.load_from_data(ASKPASS_CSS)
        Gtk.StyleContext.add_provider_for_screen(
            Gdk.Screen.get_default(), css,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

        self.window = Gtk.Window(title="Proxy GUI — Autenticación")
        self.window.set_default_size(380, 170)
        self.window.set_resizable(False)
        self.window.set_position(Gtk.WindowPosition.CENTER)
        self.window.set_modal(True)
        self.window.connect("delete-event", lambda *a: sys.exit(1))
        self.window.set_type_hint(Gdk.WindowTypeHint.DIALOG)

        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=14)
        vbox.set_margin_start(20)
        vbox.set_margin_end(20)
        vbox.set_margin_top(20)
        vbox.set_margin_bottom(20)
        self.window.add(vbox)

        lbl = Gtk.Label()
        lbl.set_markup(
            '<span font_size="12" weight="bold">Permisos de administrador</span>'
        )
        lbl.set_halign(Gtk.Align.START)
        vbox.pack_start(lbl, False, False, 0)

        desc = Gtk.Label()
        desc.set_markup(
            '<span font_size="11" color="#6c7086">Proxy GUI necesita permisos de'
            ' administrador para configurar el proxy en el sistema.</span>'
        )
        desc.set_halign(Gtk.Align.START)
        desc.set_line_wrap(True)
        vbox.pack_start(desc, False, False, 0)

        self.entry = Gtk.Entry()
        self.entry.set_visibility(False)
        self.entry.set_placeholder_text("Contraseña de sudo")
        self.entry.set_input_purpose(Gtk.InputPurpose.PASSWORD)
        vbox.pack_start(self.entry, False, False, 0)

        bbox = Gtk.Box(spacing=8)
        bbox.set_halign(Gtk.Align.END)
        bbox.set_margin_top(4)
        vbox.pack_start(bbox, False, False, 0)

        cancel = Gtk.Button(label="Cancelar")
        cancel.connect("clicked", lambda *a: sys.exit(1))
        bbox.pack_start(cancel, False, False, 0)

        ok = Gtk.Button(label="Autenticar")
        ok.get_style_context().add_class("suggested-action")
        ok.connect("clicked", self._on_ok)
        ok.set_can_default(True)
        ok.grab_default()
        bbox.pack_start(ok, False, False, 0)

        self.entry.connect("activate", self._on_ok)

        self.window.show_all()
        self.entry.grab_focus()

    def _on_ok(self, *a):
        self.password = self.entry.get_text()
        Gtk.main_quit()

    def run(self):
        Gtk.main()
        return self.password


if __name__ == "__main__":
    dlg = AskPassDialog()
    password = dlg.run()
    if password:
        print(password)
    else:
        sys.exit(1)
