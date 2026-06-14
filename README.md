# Proxy GUI

> System tray proxy toggle for Linux. One click to enable/disable your corporate proxy.

![Proxy GUI](screenshot.png)

## Features

- **System tray icon** — green when proxy is on, red when off
- **One-click toggle** — left click to enable/disable
- **Right-click menu** — Activate, Deactivate, Auto-detect, Configure
- **Configuration window** — edit proxy settings with a GUI
- **Desktop notifications** — alerts on state changes
- **Auto-start** — launches on login

## Requirements

- Python 3.10+
- GTK 3 + AppIndicator (usually pre-installed on Ubuntu/Pop!_OS)

```bash
sudo apt install python3-gi python3-gi-cairo gir1.2-gtk-3.0 gir1.2-appindicator3-0.1 libnotify-bin
```

## Install

### From PyPI

```bash
pip install --user proxy-gui
```

### From .deb

Download the latest `.deb` from [Releases](https://github.com/marcossd/proxy-gui/releases).

```bash
sudo dpkg -i proxy-gui_1.0.0_all.deb
```

### From source

```bash
git clone https://github.com/marcossd/proxy-gui.git
cd proxy-gui
make install
```

## Run

```bash
proxy-gui
```

Or launch from your application menu.

For auto-start on login:

```bash
mkdir -p ~/.config/autostart
cp /usr/local/share/applications/proxy-gui.desktop ~/.config/autostart/
```

## Configuration

The app reads and writes `~/.config/proxy/proxy.conf` — the same file used by the [proxy](https://github.com/marcossd/proxy) script.

## How it works

1. **proxy-local.py** — a lightweight Python proxy that listens on `127.0.0.1:3128`
2. Forwards requests to your corporate proxy with `Proxy-Authorization: Basic`
3. Your apps connect to `127.0.0.1:3128` without needing credentials

## Build .deb

```bash
make deb
```

## License

MIT
