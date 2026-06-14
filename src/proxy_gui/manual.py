"""User manual window."""

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk


TEXT = """\
NovaProxy Manager — Manual de usuario
=======================================

NovaProxy Manager es un gestor de proxy corporativo con interfaz
gráfica y línea de comandos. Permite activar/desactivar el proxy
con un solo clic y gestionar múltiples perfiles de configuración.


┌─────────────────────────────────────────────────────────────┐
│ 1. USO BÁSICO (Interfaz gráfica)                           │
└─────────────────────────────────────────────────────────────┘

  • Toggle: botón central para activar/desactivar el proxy.
  • Hamburguesa ☰ (esquina superior derecha): acceso rápido a
    Configuración, Acerca de, Perfiles y Manual.
  • Bandeja del sistema: icono en el panel con menú contextual.
  • Configuración: establece Host, Puerto, Usuario y Contraseña
    del proxy corporativo, y dominios excluidos (No Proxy).


┌─────────────────────────────────────────────────────────────┐
│ 2. PERFILES DE CONFIGURACIÓN                               │
└─────────────────────────────────────────────────────────────┘

  Los perfiles permiten tener distintas configuraciones de
  proxy y cambiar entre ellas al instante.

  • Crear perfil: Perfiles → Nuevo → completar datos.
  • Aplicar perfil: seleccionar → Aplicar perfil.
    (Esto escribe proxy.conf y ejecuta novapm-bash apply)
  • Eliminar: marcar con checkbox → Eliminar.
  • Editar contenido: aplicar el perfil → Configuración →
    modificar campos → Guardar y aplicar.

  Los perfiles se almacenan en:
    ~/.config/proxy/profiles.json


┌─────────────────────────────────────────────────────────────┐
│ 3. LÍNEA DE COMANDOS (CLI)                                 │
└─────────────────────────────────────────────────────────────┘

  novapm              Abre la interfaz gráfica.

  novapm on           Activa el proxy (solicita sudo con
                      diálogo gráfico).

  novapm off          Desactiva el proxy.

  novapm status       Muestra el estado actual del proxy
                      (encendido/apagado y variables de entorno).

  Nota: los comandos on/off/status ejecutan el script interno
  novapm-bash, que configura las reglas de iptables y las
  variables de entorno del sistema.


┌─────────────────────────────────────────────────────────────┐
│ 4. ARCHIVOS Y UBICACIONES                                  │
└─────────────────────────────────────────────────────────────┘

  Configuración:
    ~/.config/proxy/proxy.conf

  Perfiles:
    ~/.config/proxy/profiles.json

  Scripts internos:
    ~/.local/bin/novapm-bash
    ~/.local/bin/novapm-local.py
    ~/.local/bin/proxy-askpass

  Servicio systemd:
    ~/.config/systemd/user/novapm-local.service

  Logs del servicio:
    journalctl --user -u novapm-local.service -f


┌─────────────────────────────────────────────────────────────┐
│ 5. SOLUCIÓN DE PROBLEMAS                                   │
└─────────────────────────────────────────────────────────────┘

  • "No se activa el proxy":
    - Verificar credenciales en Configuración.
    - Comprobar conectividad con el host proxy.

  • "Error de permisos (sudo)":
    - El diálogo AskPass debe mostrar el campo de contraseña.
    - Si no aparece, instalar: sudo apt install ssh-askpass

  • "El icono del sistema no aparece":
    - Asegurar que AyatanaAppIndicator3 está instalado:
      sudo apt install gir1.2-ayatanaappindicator3-0.1

  • "Los cambios no se aplican":
    - Usar "Guardar y aplicar" en Configuración.
    - O desactivar y volver a activar el proxy.


NovaProxy Manager v1.2.0
"""


def show_manual(parent):
    css = Gtk.CssProvider()
    css.load_from_data(b"""
    textview.manual-view {
        font-family: monospace;
        font-size: 13px;
        padding: 16px;
    }
    """)
    Gtk.StyleContext.add_provider_for_screen(
        Gdk.Screen.get_default(), css,
        Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
    )

    win = Gtk.Window(title="NovaProxy — Manual de usuario")
    win.set_default_size(560, 500)
    win.set_position(Gtk.WindowPosition.CENTER_ON_PARENT)
    win.set_transient_for(parent)
    win.set_resizable(True)

    scrolled = Gtk.ScrolledWindow()
    scrolled.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
    win.add(scrolled)

    buf = Gtk.TextBuffer()
    buf.set_text(TEXT)

    tv = Gtk.TextView(buffer=buf)
    tv.set_editable(False)
    tv.set_cursor_visible(False)
    tv.set_wrap_mode(Gtk.WrapMode.WORD)
    tv.get_style_context().add_class("manual-view")
    tv.set_margin_start(16)
    tv.set_margin_end(16)
    tv.set_margin_top(16)
    tv.set_margin_bottom(16)
    scrolled.add(tv)

    win.show_all()
