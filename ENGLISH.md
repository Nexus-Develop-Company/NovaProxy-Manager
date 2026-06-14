<p align="center">
  <img src="src/proxy_gui/icons/novapm.svg" width="96" height="96" alt="NovaProxy Manager">
</p>

<h1 align="center">NovaProxy Manager</h1>

<p align="center">
  Corporate proxy manager — GUI + CLI
  <br>
  <a href="https://github.com/Nexus-Develop-Company/NovaProxy-Manager/wiki">📖 Wiki</a>
  •
  <a href="README.md">🇪🇸 Español</a>
</p>

---

## ✨ Features

- **ON/OFF toggle** — enable/disable proxy with one click
- **System tray** — green (on) / gray (off) icon, contextual menu with profiles
- **Multiple profiles** — different setups for different workplaces
- **Sidebar** — quick access to Settings, Profiles, Manual
- **CLI** — `novapm on`, `novapm off`, `novapm status`
- **Local tunnel** — local proxy with Basic auth forwarding to your corporate proxy

## ⚡ Quick install

### From .deb
```bash
sudo apt install ./novapm_1.0.0-1_all.deb
```

### From APT repo
```bash
sudo mkdir -p /usr/share/keyrings
sudo curl -fsSLo /usr/share/keyrings/novapm.gpg \
  https://raw.githubusercontent.com/Nexus-Develop-Company/NovaProxy-Manager/main/data/novapm.gpg
echo "deb [signed-by=/usr/share/keyrings/novapm.gpg] https://nexus-develop-company.github.io/NovaProxy-Manager/apt/ stable main" | sudo tee /etc/apt/sources.list.d/novapm.list
sudo apt update
sudo apt install novapm
```

### install.sh script
```bash
bash <(curl -s https://raw.githubusercontent.com/Nexus-Develop-Company/NovaProxy-Manager/main/install.sh)
```

### pipx
```bash
pipx install --system-site-packages git+https://github.com/Nexus-Develop-Company/NovaProxy-Manager.git
```

## 🚀 Usage

```bash
novapm          # Open the GUI
novapm on       # Enable proxy
novapm off      # Disable proxy
novapm status   # Show status
```

## 📁 Profiles

Create different proxy configurations for different workplaces. Go to **Profiles** from the sidebar or system tray.

Profiles are stored in `~/.config/proxy/profiles.json`.

## 📚 More info

Check the [Wiki](https://github.com/Nexus-Develop-Company/NovaProxy-Manager/wiki) for detailed documentation: installation, configuration, troubleshooting, and development guide.

## 🛠 Development

```bash
git clone https://github.com/Nexus-Develop-Company/NovaProxy-Manager.git
cd NovaProxy-Manager
make install   # install via pipx
make deb       # build .deb
```

## 📄 License

MIT — Nexus Develop Company
