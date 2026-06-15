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

Elegí el método que prefieras:

### 📦 Opción 1: Desde .deb

1. Descargá el archivo `.deb` desde [GitHub Releases](https://github.com/Nexus-Develop-Company/NovaProxy-Manager/releases)
2. Instalalo:
   ```bash
   sudo apt install ./novapm_1.0.0-1_all.deb
   ```

> 💡 Si ya clonaste el repositorio, el `.deb` está en `dist/novapm_1.0.0-1_all.deb`

### 📦 Opción 2: Desde APT repo (recomendada)

```bash
# 1. Descargar la clave GPG
sudo mkdir -p /usr/share/keyrings
sudo curl -fsSLo /usr/share/keyrings/novapm.gpg \
  https://github.com/Nexus-Develop-Company/NovaProxy-Manager/releases/latest/download/novapm.gpg

# 2. Agregar el repositorio
echo "deb [signed-by=/usr/share/keyrings/novapm.gpg] https://nexus-develop-company.github.io/NovaProxy-Manager/apt/ stable main" | sudo tee /etc/apt/sources.list.d/novapm.list

# 3. Instalar
sudo apt update
sudo apt install novapm
```

> ⚠️ Si estás detrás de un proxy corporativo, configurá la variable `http_proxy` antes del curl o copiá la clave desde el repositorio clonado: `sudo cp data/novapm.gpg /usr/share/keyrings/novapm.gpg`

### 📦 Opción 3: Script install.sh (automático)

```bash
bash <(curl -s https://raw.githubusercontent.com/Nexus-Develop-Company/NovaProxy-Manager/main/install.sh)
```

### 📦 Opción 4: pipx (desde GitHub)

```bash
pipx install --system-site-packages git+https://github.com/Nexus-Develop-Company/NovaProxy-Manager.git
```

### 📦 Opción 5: Compilar desde fuente

```bash
git clone https://github.com/Nexus-Develop-Company/NovaProxy-Manager.git
cd NovaProxy-Manager
make install
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

### Automática (recomendada)
```bash
novapm uninstall
```
Elimina todo: pipx, scripts, systemd, configuración, desktop, iconos.

### Manual según método de instalación

| Método | Comando |
|--------|---------|
| **APT repo** | `sudo apt remove novapm && sudo rm /etc/apt/sources.list.d/novapm.list` |
| **.deb** | `sudo apt remove novapm` |
| **pipx** | `pipx uninstall novapm` |
| **install.sh** | `pipx uninstall novapm` |

Si desinstalaste manual y querés borrar la configuración:
```bash
rm -rf ~/.config/proxy ~/.local/bin/novapm* ~/.config/systemd/user/novapm*
```

## 🛠 Desarrollo

```bash
git clone https://github.com/Nexus-Develop-Company/NovaProxy-Manager.git
cd NovaProxy-Manager
make install   # instala con pipx
make deb       # compila .deb
```

## 📄 Licencia

MIT — Nexus Develop Company
