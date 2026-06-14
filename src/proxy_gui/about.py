"""About dialog for Proxy GUI."""

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GLib


def show_about(parent=None):
    dialog = Gtk.AboutDialog()
    dialog.set_transient_for(parent)
    dialog.set_program_name("NovaProxy Manager")
    dialog.set_version("1.0.0")
    dialog.set_comments("Gestor de proxy corporativo con interfaz gráfica")

    _mit = getattr(Gtk.License, "MIT_X11", getattr(Gtk.License, "MIT", None))
    if _mit is not None:
        dialog.set_license_type(_mit)

    dialog.set_copyright("© 2026 Nexus Develop Company")
    dialog.set_website("https://github.com/Nexus-Develop-Company/NovaProxy-Manager.git")
    dialog.set_website_label("GitHub")
    dialog.set_logo(None)

    dialog.set_comments(
        "NovaProxy Manager permite activar y desactivar el proxy "
        "corporativo con un solo clic.\n\n"
        "Tunel Local: 127.0.0.1:3128  |  "
        "Host Proxy: configurable en Ajustes\n"
        "Usa autenticación Basic hacia el proxy corporativo.\n\n"
        "─── Créditos ───\n\n"
        "NovaProxy Manager fue desarrollado por Marcos Santana, "
        "único miembro del staff y desarrollador principal del proyecto. "
        "Este software está diseñado para facilitar la gestión del proxy "
        "corporativo en entornos Linux, brindando una experiencia sencilla "
        "y eficiente a través de una interfaz gráfica moderna.\n\n"
        "Contacto:\n"
        "  • Teléfono: +5355620975\n"
        "  • Correo: marcosjaviersantana300302@gmail.com"
    )

    dialog.connect("response", lambda d, _: d.destroy())
    dialog.show()
