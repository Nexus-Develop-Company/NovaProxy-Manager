"""Profile management window — CRUD + switch profiles."""

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk, GLib

from .profiles import ProfileManager


STYLE = b"""
.profile-active {
    color: #2ecc71;
    font-weight: bold;
    font-size: 11px;
}
.profile-name {
    font-size: 14px;
}
.profile-detail {
    font-size: 11px;
}
"""


def _profile_dialog(parent, title, initial=None):
    dialog = Gtk.Dialog(
        title=title,
        transient_for=parent,
        modal=True,
        flags=0,
    )
    dialog.set_default_size(400, 320)
    dialog.add_button("Cancelar", Gtk.ResponseType.CANCEL)
    dialog.add_button("Guardar", Gtk.ResponseType.OK)
    dialog.set_default_response(Gtk.ResponseType.OK)

    box = dialog.get_content_area()
    box.set_margin_start(16)
    box.set_margin_end(16)
    box.set_margin_top(16)
    box.set_margin_bottom(16)
    box.set_spacing(8)

    fields = [
        ("name", "Nombre del perfil:", True),
        ("UPSTREAM_HOST", "Proxy Host:", True),
        ("UPSTREAM_PORT", "Proxy Port:", True),
        ("UPSTREAM_USER", "User:", False),
        ("UPSTREAM_PASS", "Password:", False),
        ("NO_PROXY", "No Proxy:", True),
    ]

    entries = {}
    for key, label, _required in fields:
        row = Gtk.Box(spacing=8)

        lbl = Gtk.Label(label=label, width_chars=16)
        lbl.set_xalign(1.0)
        lbl.get_style_context().add_class("dim-label")

        entry = Gtk.Entry()
        entry.set_hexpand(True)
        if key == "UPSTREAM_PASS":
            entry.set_visibility(False)
            entry.set_input_purpose(Gtk.InputPurpose.PASSWORD)
        if initial and key in initial:
            entry.set_text(initial[key])

        entries[key] = entry
        row.pack_start(lbl, False, False, 0)
        row.pack_start(entry, True, True, 0)
        box.pack_start(row, False, False, 0)

    dialog.show_all()
    response = dialog.run()
    result = None
    if response == Gtk.ResponseType.OK:
        result = {}
        for key in fields:
            k = key[0]
            result[k] = entries[k].get_text().strip()
            if key[2] and not result[k]:
                result = None
                break
    dialog.destroy()
    return result


class ProfilesWindow:
    def __init__(self, parent, on_switch=None, on_change=None):
        self.parent = parent
        self.on_switch = on_switch
        self.on_change = on_change
        self.pm = ProfileManager()
        self._checked = set()
        self._build()

    def _build(self):
        css = Gtk.CssProvider()
        css.load_from_data(STYLE)
        Gtk.StyleContext.add_provider_for_screen(
            Gdk.Screen.get_default(), css,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

        self.window = Gtk.Window(title="Perfiles de configuración")
        self.window.set_default_size(420, 380)
        self.window.set_resizable(False)
        self.window.set_position(Gtk.WindowPosition.CENTER_ON_PARENT)
        self.window.set_transient_for(self.parent)
        self.window.connect("delete-event", lambda *a: self.window.destroy())

        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.window.add(vbox)

        title = Gtk.Label()
        title.set_markup('<span font_size="16" weight="bold">Perfiles de configuración</span>')
        title.set_halign(Gtk.Align.START)
        title.set_margin_start(16)
        title.set_margin_top(16)
        title.set_margin_bottom(4)
        vbox.pack_start(title, False, False, 0)

        desc = Gtk.Label(label="Creá y gestioná perfiles. El contenido se edita en Configuración.")
        desc.set_halign(Gtk.Align.START)
        desc.get_style_context().add_class("dim-label")
        desc.set_margin_start(16)
        desc.set_margin_bottom(12)
        vbox.pack_start(desc, False, False, 0)

        scrolled = Gtk.ScrolledWindow()
        scrolled.set_min_content_height(180)
        scrolled.set_vexpand(True)
        vbox.pack_start(scrolled, True, True, 0)

        self.listbox = Gtk.ListBox()
        self.listbox.set_selection_mode(Gtk.SelectionMode.SINGLE)
        scrolled.add(self.listbox)

        bbox = Gtk.Box(spacing=8)
        bbox.set_margin_start(16)
        bbox.set_margin_end(16)
        bbox.set_margin_top(12)
        bbox.set_margin_bottom(16)
        bbox.set_halign(Gtk.Align.CENTER)
        vbox.pack_start(bbox, False, False, 0)

        for label, cb in [
            ("Nuevo", self._on_new),
            ("Eliminar", self._on_delete),
        ]:
            btn = Gtk.Button(label=label)
            btn.connect("clicked", cb)
            bbox.pack_start(btn, False, False, 0)

        apply_btn = Gtk.Button(label="Aplicar perfil")
        apply_btn.get_style_context().add_class("suggested-action")
        apply_btn.connect("clicked", self._on_apply)
        bbox.pack_start(apply_btn, False, False, 0)

        self.apply_status = Gtk.Label()
        self.apply_status.set_halign(Gtk.Align.CENTER)
        self.apply_status.set_margin_bottom(12)
        vbox.pack_start(self.apply_status, False, False, 0)

        self._refresh()

    def _build_row(self, name):
        config = self.pm.get(name)
        current = self.pm.current()

        row = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=1)
        row.set_margin_start(4)
        row.set_margin_end(12)
        row.set_margin_top(8)
        row.set_margin_bottom(8)
        row._profile_name = name

        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)

        check = Gtk.CheckButton()
        check.connect("toggled", lambda cb, n=name: self._on_check_toggle(n, cb.get_active()))
        hbox.pack_start(check, False, False, 0)

        name_lbl = Gtk.Label(label=name)
        name_lbl.get_style_context().add_class("profile-name")
        name_lbl.set_halign(Gtk.Align.START)
        name_lbl.set_hexpand(True)
        hbox.pack_start(name_lbl, True, True, 0)

        if name == current:
            badge = Gtk.Label(label="● ACTIVO")
            badge.get_style_context().add_class("profile-active")
            hbox.pack_end(badge, False, False, 0)

        row.pack_start(hbox, False, False, 0)

        detail = Gtk.Label(
            label=f"{config.get('UPSTREAM_HOST', '?')}:{config.get('UPSTREAM_PORT', '?')}"
        )
        detail.get_style_context().add_class("dim-label")
        detail.get_style_context().add_class("profile-detail")
        detail.set_halign(Gtk.Align.START)
        detail.set_margin_start(36)
        row.pack_start(detail, False, False, 0)

        return row

    def _refresh(self):
        row = self.listbox.get_row_at_index(0)
        while row is not None:
            self.listbox.remove(row)
            row = self.listbox.get_row_at_index(0)

        self._checked.clear()

        profiles = self.pm.list()
        for name in profiles:
            row = self._build_row(name)
            self.listbox.insert(row, -1)

        self.listbox.show_all()

        if not profiles:
            empty = Gtk.Label(label="No hay perfiles. Creá uno nuevo.")
            empty.set_margin_top(20)
            empty.set_margin_bottom(20)
            empty.get_style_context().add_class("dim-label")
            self.listbox.insert(empty, -1)
            self.listbox.show_all()

    def _on_check_toggle(self, name, active):
        if active:
            self._checked.add(name)
        else:
            self._checked.discard(name)

    def _selected_profile(self):
        row = self.listbox.get_selected_row()
        if row is None:
            return None
        return self._name_from_row(row)

    def _name_from_row(self, row):
        child = row.get_child()
        if child is None:
            return None
        return getattr(child, "_profile_name", None)

    def _on_new(self, _btn):
        result = _profile_dialog(self.window, "Nuevo perfil")
        if result and result.get("name"):
            config = {
                "UPSTREAM_HOST": result.get("UPSTREAM_HOST", ""),
                "UPSTREAM_PORT": result.get("UPSTREAM_PORT", ""),
                "UPSTREAM_USER": result.get("UPSTREAM_USER", ""),
                "UPSTREAM_PASS": result.get("UPSTREAM_PASS", ""),
                "NO_PROXY": result.get("NO_PROXY", ""),
            }
            self.pm.save(result["name"], config)
            self._refresh()
            if self.on_change:
                self.on_change()

    def _on_delete(self, _btn):
        targets = set()
        for name in self._checked:
            targets.add(name)
        if not targets:
            sel = self._selected_profile()
            if sel:
                targets.add(sel)
        if not targets:
            return

        active = self.pm.current()
        blocked = [n for n in targets if n == active]
        can_delete = [n for n in targets if n != active]

        if blocked:
            dialog = Gtk.MessageDialog(
                transient_for=self.window,
                flags=0,
                message_type=Gtk.MessageType.WARNING,
                buttons=Gtk.ButtonsType.OK,
                text="No se puede eliminar el perfil activo",
            )
            dialog.format_secondary_text(
                "Cambiá a otro perfil antes de eliminar «{}».".format(blocked[0])
            )
            dialog.run()
            dialog.destroy()
            if not can_delete:
                return

        count = len(can_delete)
        names = ", ".join(can_delete)
        dialog = Gtk.MessageDialog(
            transient_for=self.window,
            flags=0,
            message_type=Gtk.MessageType.QUESTION,
            buttons=Gtk.ButtonsType.YES_NO,
            text=f"¿Eliminar {count} perfil(es)?",
        )
        dialog.format_secondary_text(names)
        response = dialog.run()
        dialog.destroy()
        if response == Gtk.ResponseType.YES:
            for name in can_delete:
                self.pm.delete(name)
            self._refresh()
            if self.on_change:
                self.on_change()

    def _on_apply(self, _btn):
        name = self._selected_profile()
        if not name:
            return
        self.apply_status.set_markup('<span foreground="#888">Aplicando…</span>')

        import threading
        def _run():
            success, output = self.pm.switch(name)
            GLib.idle_add(self._apply_done, success, output, name)
        threading.Thread(target=_run, daemon=True).start()

    def _apply_done(self, success, output, name):
        self.apply_status.set_markup("")
        if not success:
            dialog = Gtk.MessageDialog(
                transient_for=self.window,
                flags=0,
                message_type=Gtk.MessageType.ERROR,
                buttons=Gtk.ButtonsType.OK,
                text="Error al aplicar perfil",
            )
            dialog.format_secondary_text(output[:200])
            dialog.run()
            dialog.destroy()
            return
        if self.on_switch:
            self.on_switch(name)
        self.window.destroy()

    def show(self):
        self.window.show_all()
