"""Main window — proton-vpn style proxy toggle."""

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk, GLib, cairo
import math
import threading

from . import proxyctl
from .notifier import notify


STYLE = b"""
button.toggle-btn {
    font-size: 15px;
    font-weight: bold;
    min-height: 46px;
    min-width: 200px;
    border-radius: 23px;
    padding: 0 32px;
    border: none;
    transition: all 200ms ease;
}
button.toggle-btn.on {
    background: linear-gradient(135deg, #2ecc71, #27ae60);
    color: #fff;
}
button.toggle-btn.on:hover {
    background: linear-gradient(135deg, #27ae60, #1e8449);
}
button.toggle-btn.off {
    background: linear-gradient(135deg, #95a5a6, #7f8c8d);
    color: #fff;
}
button.toggle-btn.off:hover {
    background: linear-gradient(135deg, #7f8c8d, #6c7a7a);
}
/* Sidebar backdrop */
.sidebar-backdrop {
    background: rgba(0, 0, 0, 0.35);
}
/* Sidebar panel */
.sidebar {
    background: @theme_bg_color;
    border-right: 1px solid @borders;
}
/* Sidebar header */
.sidebar-header {
    padding: 20px 16px 4px 20px;
    font-size: 15px;
    font-weight: bold;
}
/* Sidebar close button */
.sidebar-close {
    background: transparent;
    border: none;
    padding: 4px;
    min-width: 0;
    color: @theme_fg_color;
    opacity: 0.6;
    font-size: 18px;
}
.sidebar-close:hover {
    opacity: 1;
    background: rgba(128,128,128,0.15);
    border-radius: 4px;
}
/* Sidebar items */
.sidebar-item {
    background: transparent;
    border: none;
    border-radius: 0;
    padding: 10px 20px;
    font-size: 13px;
    color: @theme_fg_color;
}
.sidebar-item:hover {
    background: @theme_selected_bg_color;
    color: @theme_selected_fg_color;
}
.sidebar-sep {
    margin: 8px 16px;
}
/* Hamburger button */
.hamburger-btn {
    background: transparent;
    border: none;
    padding: 8px;
    min-width: 36px;
    min-height: 36px;
    color: @theme_fg_color;
    font-size: 18px;
}
.hamburger-btn:hover {
    background: rgba(128,128,128,0.15);
    border-radius: 6px;
}
"""


class StatusCircle(Gtk.DrawingArea):
    def __init__(self, size=110):
        super().__init__()
        self.set_size_request(size, size)
        self.set_halign(Gtk.Align.CENTER)
        self.set_valign(Gtk.Align.CENTER)
        self.status = False
        self.connect("draw", self._draw)

    def set_status(self, on: bool):
        self.status = on
        self.queue_draw()

    def _draw(self, widget, cr: cairo.Context):
        alloc = widget.get_allocation()
        cx, cy = alloc.width / 2, alloc.height / 2
        radius = min(cx, cy) - 4

        # Outer glow
        if self.status:
            cr.set_source_rgba(0.18, 0.80, 0.44, 0.12)
        else:
            cr.set_source_rgba(0.58, 0.63, 0.65, 0.12)
        cr.arc(cx, cy, radius + 10, 0, 2 * math.pi)
        cr.fill()

        # Main circle
        if self.status:
            cr.set_source_rgb(0.18, 0.80, 0.44)
        else:
            cr.set_source_rgb(0.58, 0.63, 0.65)
        cr.arc(cx, cy, radius, 0, 2 * math.pi)
        cr.fill()

        # Highlight (top-left light reflection)
        cr.set_source_rgba(1, 1, 1, 0.25)
        cr.arc(cx - radius * 0.3, cy - radius * 0.3, radius * 0.28, 0, 2 * math.pi)
        cr.fill()

        # Icon
        cr.set_source_rgb(1, 1, 1)
        cr.set_line_width(4.5)
        cr.set_line_cap(cairo.LineCap.ROUND)
        cr.set_line_join(cairo.LineJoin.ROUND)

        if self.status:
            r2 = radius * 0.35
            cr.move_to(cx - r2, cy)
            cr.line_to(cx - r2 * 0.3, cy + r2 * 0.8)
            cr.line_to(cx + r2 * 1.2, cy - r2 * 0.6)
            cr.stroke()
        else:
            s = radius * 0.3
            cr.move_to(cx - s, cy - s)
            cr.line_to(cx + s, cy + s)
            cr.move_to(cx + s, cy - s)
            cr.line_to(cx - s, cy + s)
            cr.stroke()


class MainWindow:
    def __init__(self):
        self.config_win = None
        self.tray = None
        self.sidebar = None
        self._last_status = None
        self._build()
        GLib.timeout_add(2000, self._poll_status)

    def set_tray(self, tray):
        self.tray = tray

    def _build(self):
        css = Gtk.CssProvider()
        css.load_from_data(STYLE)
        Gtk.StyleContext.add_provider_for_screen(
            Gdk.Screen.get_default(), css,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

        self.window = Gtk.Window(title="NovaProxy Manager")
        self.window.set_default_size(300, 500)
        self.window.set_resizable(False)
        self.window.set_position(Gtk.WindowPosition.CENTER)
        self.window.connect("delete-event", lambda w, e: w.hide() or True)
        self.window.connect("show", lambda *a: self._update_ui())

        # Set window icon
        import os as _os
        _icon = _os.path.join(_os.path.dirname(__file__), "icons", "novapm-on.png")
        if _os.path.exists(_icon):
            self.window.set_icon_from_file(_icon)

        self.window.set_gravity(Gdk.Gravity.CENTER)

        # Overlay to allow sidebar on top of content
        overlay = Gtk.Overlay()
        self.window.add(overlay)

        # --- MAIN CONTENT (Centered) ---
        main_container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        main_container.set_valign(Gtk.Align.CENTER)
        main_container.set_halign(Gtk.Align.CENTER)
        main_container.set_hexpand(True)
        main_container.set_vexpand(True)
        overlay.add(main_container)

        # Header
        header = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        header.set_halign(Gtk.Align.CENTER)
        header.set_margin_bottom(30)
        
        title_lbl = Gtk.Label()
        title_lbl.set_markup('<span font_size="22" weight="bold">NovaProxy Manager</span>')
        title_lbl.set_halign(Gtk.Align.CENTER)
        header.pack_start(title_lbl, False, False, 0)

        sub_lbl = Gtk.Label(label="Gestor de proxy corporativo")
        sub_lbl.get_style_context().add_class("dim-label")
        sub_lbl.set_halign(Gtk.Align.CENTER)
        header.pack_start(sub_lbl, False, False, 0)
        main_container.pack_start(header, False, False, 0)

        # Status Circle
        self.status_circle = StatusCircle(110)
        main_container.pack_start(self.status_circle, False, False, 0)

        # Status Labels
        sbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        sbox.set_halign(Gtk.Align.CENTER)
        sbox.set_margin_bottom(30)
        main_container.pack_start(sbox, False, False, 0)

        self.status_label = Gtk.Label()
        self.status_label.set_markup('<span font_size="14" weight="bold">—</span>')
        self.status_label.set_halign(Gtk.Align.CENTER)
        sbox.pack_start(self.status_label, False, False, 0)

        self.info_label = Gtk.Label()
        self.info_label.get_style_context().add_class("dim-label")
        self.info_label.set_halign(Gtk.Align.CENTER)
        sbox.pack_start(self.info_label, False, False, 0)

        # Toggle Button
        self.toggle_btn = Gtk.Button(label="—")
        self.toggle_btn.get_style_context().add_class("toggle-btn")
        self.toggle_btn.set_halign(Gtk.Align.CENTER)
        self.toggle_btn.connect("clicked", self._on_toggle)
        main_container.pack_start(self.toggle_btn, False, False, 0)

        # --- SIDEBAR BACKDROP ---
        self.sidebar_backdrop = Gtk.EventBox()
        self.sidebar_backdrop.get_style_context().add_class("sidebar-backdrop")
        self.sidebar_backdrop.set_hexpand(True)
        self.sidebar_backdrop.set_vexpand(True)
        self.sidebar_backdrop.connect("button-press-event", lambda *a: self._toggle_sidebar())
        self.backdrop_revealer = Gtk.Revealer()
        self.backdrop_revealer.set_transition_type(Gtk.RevealerTransitionType.CROSSFADE)
        self.backdrop_revealer.set_transition_duration(200)
        self.backdrop_revealer.add(self.sidebar_backdrop)
        overlay.add_overlay(self.backdrop_revealer)

        # --- SIDEBAR PANEL ---
        self.sidebar = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.sidebar.set_size_request(150, -1)
        self.sidebar.set_hexpand(False)
        self.sidebar.set_vexpand(True)
        self.sidebar.get_style_context().add_class("sidebar")

        # Sidebar header row
        hdr = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        hdr.set_margin_start(16)
        hdr.set_margin_end(16)
        hdr.set_margin_top(16)
        hdr.set_margin_bottom(12)
        lbl = Gtk.Label(label="NovaProxy")
        lbl.get_style_context().add_class("sidebar-header")
        lbl.set_halign(Gtk.Align.START)
        hdr.pack_start(lbl, False, False, 0)
        self.sidebar.pack_start(hdr, False, False, 0)

        self.sidebar.pack_start(Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL), False, False, 0)

        # Sidebar items
        items_data = [
            ("⚙", "Configuración", lambda *a: self._on_open_config()),
            ("ℹ", "Acerca de", lambda *a: self._on_about(None)),
            ("📁", "Perfiles", lambda *a: self._on_profiles()),
        ]
        sub_items = [
            ("📖", "Manual", lambda *a: self._on_manual()),
            ("🔄", "Actualizar", lambda *a: self._on_update()),
        ]
        for icon, label, cb in items_data:
            btn = Gtk.Button(label=f"{icon}  {label}")
            btn.get_style_context().add_class("sidebar-item")
            btn.set_halign(Gtk.Align.FILL)
            btn.connect("clicked", lambda *a, c=cb: (self._toggle_sidebar(), c()))
            self.sidebar.pack_start(btn, False, False, 0)

        self.sidebar.pack_start(Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL), False, False, 0)

        for icon, label, cb in sub_items:
            btn = Gtk.Button(label=f"{icon}  {label}")
            btn.get_style_context().add_class("sidebar-item")
            btn.set_halign(Gtk.Align.FILL)
            btn.connect("clicked", lambda *a, c=cb: (self._toggle_sidebar(), c()))
            self.sidebar.pack_start(btn, False, False, 0)

        sep = Gtk.Box()
        sep.set_vexpand(True)
        self.sidebar.pack_start(sep, True, True, 0)

        btn_uninstall = Gtk.Button(label="🗑  Desinstalar")
        btn_uninstall.get_style_context().add_class("sidebar-item")
        btn_uninstall.set_halign(Gtk.Align.FILL)
        btn_uninstall.connect("clicked", lambda *a: (self._toggle_sidebar(), self._on_uninstall()))
        self.sidebar.pack_start(btn_uninstall, False, False, 0)

        btn_quit = Gtk.Button(label="✕  Salir")
        btn_quit.get_style_context().add_class("sidebar-item")
        btn_quit.set_halign(Gtk.Align.FILL)
        btn_quit.connect("clicked", lambda *a: self._on_quit())
        self.sidebar.pack_start(btn_quit, False, False, 0)

        self.sidebar.pack_start(Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL), False, False, 0)

        empty = Gtk.Box()
        empty.set_size_request(-1, 8)
        self.sidebar.pack_end(empty, False, False, 0)

        self.sidebar_revealer = Gtk.Revealer()
        self.sidebar_revealer.set_transition_type(Gtk.RevealerTransitionType.SLIDE_RIGHT)
        self.sidebar_revealer.set_transition_duration(200)
        self.sidebar_revealer.set_halign(Gtk.Align.START)
        self.sidebar_revealer.add(self.sidebar)
        overlay.add_overlay(self.sidebar_revealer)

        # Hamburger Button (top-right corner)
        self.hamburger_btn = Gtk.Button(label="☰")
        self.hamburger_btn.get_style_context().add_class("hamburger-btn")
        self.hamburger_btn.set_margin_top(8)
        self.hamburger_btn.set_margin_end(8)
        self.hamburger_btn.connect("clicked", self._toggle_sidebar)
        hamburger_container = Gtk.Box()
        hamburger_container.set_halign(Gtk.Align.END)
        hamburger_container.set_valign(Gtk.Align.START)
        hamburger_container.pack_start(self.hamburger_btn, False, False, 0)
        overlay.add_overlay(hamburger_container)

        self._update_ui()

    def show(self):
        self.window.show_all()
        self.backdrop_revealer.set_reveal_child(False)
        self.sidebar_revealer.set_reveal_child(False)

    def _toggle_sidebar(self, _btn=None):
        visible = not self.sidebar_revealer.get_reveal_child()
        self.backdrop_revealer.set_reveal_child(visible)
        self.sidebar_revealer.set_reveal_child(visible)
        self.hamburger_btn.set_label("✕" if visible else "☰")

    def _update_ui(self):
        running = proxyctl.is_proxy_local_running()
        ctx = self.toggle_btn.get_style_context()
        ctx.remove_class("on")
        ctx.remove_class("off")
        self.status_circle.set_status(running)

        if running:
            self.status_label.set_markup(
                '<span foreground="#2ecc71" font_size="14" weight="bold">● Activado</span>'
            )
            self.info_label.set_label(f"Tunel Nova en {proxyctl.parse_config().get('PROXY_HOST', '127.0.0.1')}:{proxyctl.parse_config().get('PROXY_PORT', '3128')}")
            self.toggle_btn.set_label("DESACTIVAR")
            ctx.add_class("on")
        else:
            self.status_label.set_markup(
                '<span foreground="#95a5a6" font_size="14" weight="bold">● Desactivado</span>'
            )
            self.info_label.set_label("Sin conexión proxy")
            self.toggle_btn.set_label("ACTIVAR")
            ctx.add_class("off")

        if self.tray:
            self.tray.update_status(running)

        self._last_status = running

    def _poll_status(self):
        running = proxyctl.is_proxy_local_running()
        if running != self._last_status:
            self._last_status = running
            self._update_ui()
        return True

    def _on_toggle(self, _btn):
        self.toggle_btn.set_sensitive(False)
        self.toggle_btn.set_label("...")
        running = proxyctl.is_proxy_local_running()

        def _run():
            if running:
                proxyctl.run_proxy("off")
                GLib.idle_add(lambda: notify("NovaProxy", "Proxy desactivado"))
            else:
                success, _ = proxyctl.run_proxy("on")
                if success:
                    GLib.idle_add(lambda: notify("NovaProxy", "Proxy activado"))
            GLib.idle_add(self._update_ui)
            GLib.idle_add(lambda: self.toggle_btn.set_sensitive(True))

        threading.Thread(target=_run, daemon=True).start()

    def _on_open_config(self):
        if self.config_win and self.config_win.window.get_visible():
            self.config_win.window.present()
            return
        from .window import ConfigWindow
        self.config_win = ConfigWindow(on_close=self._on_config_closed)
        self.config_win.show()

    def _on_config_closed(self):
        self.config_win = None
        self._update_ui()

    def _on_about(self, _btn):
        from .about import show_about
        show_about(self.window)

    def _on_profiles(self):
        from .profiles_window import ProfilesWindow

        def _refresh_all(*args):
            self._update_ui()
            if self.tray:
                self.tray._rebuild_menu()

        pw = ProfilesWindow(self.window, on_switch=_refresh_all, on_change=_refresh_all)
        pw.show()

    def _on_manual(self):
        from .manual import show_manual
        show_manual(self.window)

    def _on_update(self):
        from .update import run_update
        run_update()

    def _on_uninstall(self):
        from .uninstall import run_uninstall
        run_uninstall()

    def _on_quit(self):
        proxyctl.run_proxy("off")
        self.window.get_application().quit()
