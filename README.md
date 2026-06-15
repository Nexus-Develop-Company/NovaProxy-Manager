<p align="center">
  <img src="src/proxy_gui/icons/novapm.svg" width="96" height="96" alt="NovaProxy Manager">
</p>

<h1 align="center">NovaProxy Manager</h1>

<p align="center">
  Gestor de proxy corporativo — interfaz gráfica + línea de comandos
  <br>
  <a href="https://github.com/Nexus-Develop-Company/NovaProxy-Manager/wiki">📖 Wiki</a>
  •
  <a href="ENGLISH.md">🇬🇧 English</a>
</p>

---

## ✨ Características

- **Toggle ON/OFF** — activá y desactivá el proxy con un clic
- **Bandeja del sistema** — icono verde (on) / gris (off), menú contextual con perfiles
- **Perfiles múltiples** — distintas configuraciones para distintos entornos
- **Sidebar** — acceso rápido a Configuración, Perfiles, Manual
- **CLI** — `novapm on`, `novapm off`, `novapm status`
- **Túnel local** — proxy local con autenticación Basic hacia tu proxy corporativo

## ⚡ Instalación rápida

### Desde .deb
```bash
sudo apt install ./novapm_1.0.0-1_all.deb
```

### Desde APT repo
```bash
sudo mkdir -p /usr/share/keyrings
sudo curl -fsSLo /usr/share/keyrings/novapm.gpg \
  https://raw.githubusercontent.com/Nexus-Develop-Company/NovaProxy-Manager/main/data/novapm.gpg
echo "deb [signed-by=/usr/share/keyrings/novapm.gpg] https://nexus-develop-company.github.io/NovaProxy-Manager/apt/ stable main" | sudo tee /etc/apt/sources.list.d/novapm.list
sudo apt update
sudo apt install novapm
```

### Script install.sh
```bash
bash <(curl -s https://raw.githubusercontent.com/Nexus-Develop-Company/NovaProxy-Manager/main/install.sh)
```

### pipx
```bash
pipx install --system-site-packages git+https://github.com/Nexus-Develop-Company/NovaProxy-Manager.git
```

## 🚀 Uso

```bash
novapm          # Abre la interfaz gráfica
novapm on       # Activa el proxy
novapm off      # Desactiva el proxy
novapm status   # Muestra el estado
```

## 📁 Perfiles

Creá distintas configuraciones de proxy para diferentes lugares de trabajo. Entrá a **Perfiles** desde el sidebar o la bandeja del sistema.

- **Nuevo**: completá host, puerto, usuario, contraseña y dominios excluidos
- **Aplicar**: seleccioná un perfil y aplicarlo al instante
- **Eliminar**: marcá con checkbox y eliminá los que no uses

Los perfiles se guardan en `~/.config/proxy/profiles.json`.

## 📚 Más información

Consultá la [Wiki](https://github.com/Nexus-Develop-Company/NovaProxy-Manager/wiki) para documentación detallada: instalación, configuración, solución de problemas y guía de desarrollo.

## ❌ Desinstalación

```bash
novapm uninstall    # Desinstalación guiada (automática)
```

O manual según el método de instalación:

| Método | Comando |
|--------|---------|
| **APT repo** | `sudo apt remove novapm` + `sudo rm /etc/apt/sources.list.d/novapm.list` |
| **.deb** | `sudo apt remove novapm` |
| **pipx** | `pipx uninstall novapm` |
| **install.sh** | `pipx uninstall novapm` |

Los archivos de configuración (`~/.config/proxy/`) se eliminan automáticamente con `novapm uninstall`.

## 🛠 Desarrollo

```bash
git clone https://github.com/Nexus-Develop-Company/NovaProxy-Manager.git
cd NovaProxy-Manager
make install   # instala con pipx
make deb       # compila .deb
```

## 📄 Licencia

MIT — Nexus Develop Company
