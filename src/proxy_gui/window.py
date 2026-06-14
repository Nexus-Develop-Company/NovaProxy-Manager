"""Configuration window for proxy settings."""

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk, GLib
import threading

from . import proxyctl
from .profiles import ProfileManager
from .notifier import notify


CONFIG_CSS = b"""
button.primary-btn {
    background: linear-gradient(135deg, #2ecc71, #27ae60);
    color: #fff;
    border: none;
    border-radius: 6px;
    padding: 8px 20px;
    font-weight: bold;
}
button.primary-btn:hover {
    background: linear-gradient(135deg, #27ae60, #1e8449);
}
button.secondary-btn {
    background: transparent;
    border: 1px solid rgba(128,128,128,0.3);
    border-radius: 6px;
    padding: 8px 20px;
}
button.secondary-btn:hover {
    background: rgba(128,128,128,0.1);
}
.profile-badge {
    color: #2ecc71;
    font-weight: bold;
}
"""


class ConfigWindow:
    def __init__(self, on_close):
        self.on_close = on_close
        self.entries = {}
        self.status_label = None
        self._build()

    def _build(self):
        css = Gtk.CssProvider()
        css.load_from_data(CONFIG_CSS)
        Gtk.StyleContext.add_provider_for_screen(
            Gdk.Screen.get_default(), css,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

        self.window = Gtk.Window(title="NovaProxy - Configuración")
        self.window.set_default_size(420, 420)
        self.window.set_resizable(False)
        self.window.set_position(Gtk.WindowPosition.CENTER_ON_PARENT)
        self.window.set_transient_for(None)
        self.window.connect("delete-event", self._on_close)

        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        vbox.set_margin_start(24)
        vbox.set_margin_end(24)
        vbox.set_margin_top(24)
        vbox.set_margin_bottom(16)
        self.window.add(vbox)

        # Title
        title = Gtk.Label()
        title.set_markup('<span font_size="16" weight="bold">Configuración del proxy</span>')
        title.set_halign(Gtk.Align.START)
        vbox.pack_start(title, False, False, 0)

        desc = Gtk.Label()
        desc.set_markup(
            '<span font_size="12" color="#888">Configuración del proxy</span>'
        )
        desc.set_halign(Gtk.Align.START)
        desc.set_margin_bottom(4)
        vbox.pack_start(desc, False, False, 0)

        self.profile_badge = Gtk.Label()
        self.profile_badge.set_halign(Gtk.Align.START)
        self.profile_badge.set_margin_bottom(12)
        vbox.pack_start(self.profile_badge, False, False, 0)

        # Fields
        fields = [
            ("UPSTREAM_HOST", "Proxy Host:", "10.12.0.205"),
            ("UPSTREAM_PORT", "Proxy Port:", "3128"),
            ("UPSTREAM_USER", "User:", None),
            ("UPSTREAM_PASS", "Password:", None),
            ("NO_PROXY", "No Proxy:", "localhost,127.0.0.1"),
        ]

        for key, label, placeholder in fields:
            box = Gtk.Box(spacing=8)
            box.set_margin_bottom(2)

            lbl = Gtk.Label(label=label, width_chars=16)
            lbl.set_xalign(1.0)
            lbl.get_style_context().add_class("dim-label")

            entry = Gtk.Entry()
            entry.set_hexpand(True)

            if key == "UPSTREAM_PASS":
                entry.set_visibility(False)
                entry.set_input_purpose(Gtk.InputPurpose.PASSWORD)
            if placeholder:
                entry.set_placeholder_text(placeholder)

            self.entries[key] = entry
            box.pack_start(lbl, False, False, 0)
            box.pack_start(entry, True, True, 0)
            vbox.pack_start(box, False, False, 0)

        # Status message
        self.status_label = Gtk.Label()
        self.status_label.set_margin_top(8)
        self.status_label.set_halign(Gtk.Align.START)
        vbox.pack_start(self.status_label, False, False, 0)

        # Buttons
        bbox = Gtk.Box(spacing=8)
        bbox.set_halign(Gtk.Align.END)
        bbox.set_margin_top(12)
        vbox.pack_start(bbox, False, False, 0)

        apply_btn = Gtk.Button(label="Guardar y aplicar")
        apply_btn.get_style_context().add_class("primary-btn")
        apply_btn.connect("clicked", self._on_apply)
        bbox.pack_start(apply_btn, False, False, 0)

        save_btn = Gtk.Button(label="Solo guardar")
        save_btn.get_style_context().add_class("secondary-btn")
        save_btn.connect("clicked", self._on_save)
        bbox.pack_start(save_btn, False, False, 0)

        close_btn = Gtk.Button(label="Cerrar")
        close_btn.get_style_context().add_class("secondary-btn")
        close_btn.connect("clicked", self._on_close)
        bbox.pack_start(close_btn, False, False, 0)

        self._load_values()

    def _load_values(self):
        cfg = proxyctl.parse_config()
        for key, entry in self.entries.items():
            val = cfg.get(key, "")
            if val:
                entry.set_text(val)
        self._update_profile_badge()

    def _update_profile_badge(self):
        pm = ProfileManager()
        current = pm.current()
        ctx = self.profile_badge.get_style_context()
        ctx.remove_class("profile-badge")
        if current:
            ctx.add_class("profile-badge")
            self.profile_badge.set_markup(f"● Perfil activo: {current}")
        else:
            self.profile_badge.set_markup(
                '<span foreground="#888">● Sin perfil — al guardar se creará "Default"</span>'
            )

    def _get_values(self) -> dict:
        return {k: e.get_text() for k, e in self.entries.items()}

    def _on_save(self, _btn=None):
        vals = self._get_values()
        proxyctl.write_config(vals)
        pm = ProfileManager()
        if not pm.list():
            pm.save("Default", vals)
            pm.set_active("Default")
        else:
            current = pm.current()
            if current and pm.exists(current):
                pm.save(current, vals)
        self._update_profile_badge()
        self.status_label.set_markup(
            '<span foreground="green">✓ Guardado</span>'
        )
        notify("NovaProxy", "Configuración guardada")

    def _on_apply(self, _btn):
        self.status_label.set_markup('<span foreground="#888">Guardando…</span>')

        def _run():
            vals = self._get_values()
            proxyctl.write_config(vals)
            pm = ProfileManager()
            if not pm.list():
                pm.save("Default", vals)
                pm.set_active("Default")
            else:
                current = pm.current()
                if current and pm.exists(current):
                    pm.save(current, vals)

            GLib.idle_add(lambda: self.status_label.set_markup(
                '<span foreground="#888">Aplicando…</span>'
            ))

            success, output = proxyctl.run_proxy("apply")

            def _done():
                self._update_profile_badge()
                if success:
                    self.status_label.set_markup(
                        '<span foreground="green">✓ Guardado y aplicado</span>'
                    )
                    notify("NovaProxy", "Configuración aplicada")
                else:
                    self.status_label.set_markup(
                        f'<span foreground="red">✗ Error: {output[:80]}</span>'
                    )
            GLib.idle_add(_done)

        threading.Thread(target=_run, daemon=True).start()

    def _on_close(self, *_args):
        if self.on_close:
            self.on_close()
        self.window.destroy()

    def show(self):
        self.window.show_all()
