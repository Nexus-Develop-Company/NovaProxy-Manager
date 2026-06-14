#!/usr/bin/env bash
set -e

# NovaProxy Manager — install.sh
# Uso: bash <(curl -s https://raw.githubusercontent.com/Nexus-Develop-Company/NovaProxy-Manager/main/install.sh)

REPO="Nexus-Develop-Company/NovaProxy-Manager"
APP="novapm"
PREFIX="${PREFIX:-/usr/local}"

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

info()  { echo -e "${BLUE}[INFO]${NC} $1"; }
ok()    { echo -e "${GREEN}[OK]${NC} $1"; }
warn()  { echo -e "${YELLOW}[WARN]${NC} $1"; }

# ---- OS detection ----
info "Detectando sistema operativo..."
if [ ! -f /etc/os-release ]; then
    warn "No se pudo detectar el SO. Continuando de todas formas..."
else
    . /etc/os-release
    info "Sistema: $NAME $VERSION_ID"
fi

# ---- Dependencies ----
info "Instalando dependencias..."
DEPS="python3-gi python3-gi-cairo gir1.2-gtk-3.0 gir1.2-ayatanaappindicator3-0.1 libayatana-appindicator3-1 libnotify-bin"

if command -v apt &>/dev/null; then
    sudo apt update -qq
    sudo apt install -y -qq $DEPS
    ok "Dependencias instaladas"
else
    warn "No se detectó apt. Instalá manualmente: $DEPS"
fi

# ---- pipx ----
if ! command -v pipx &>/dev/null; then
    info "Instalando pipx..."
    if command -v apt &>/dev/null; then
        sudo apt install -y -qq pipx
    else
        pip3 install --user pipx
    fi
    pipx ensurepath
    ok "pipx instalado"
fi

# ---- Install novapm ----
info "Instalando $APP..."
if pipx install --system-site-packages "git+https://github.com/$REPO.git" 2>/dev/null; then
    ok "$APP instalado via pipx"
else
    info "Falló la instalación desde git. Probando desde el directorio local..."
    if [ -f pyproject.toml ]; then
        pipx install --system-site-packages .
        ok "$APP instalado desde local"
    else
        echo -e "${YELLOW}[ERROR]${NC} No se pudo instalar. Cloná el repo y ejecutá: make install"
        exit 1
    fi
fi

# ---- Desktop file ----
info "Instalando .desktop e iconos..."
TMPDIR=$(mktemp -d)
cleanup() { rm -rf "$TMPDIR"; }
trap cleanup EXIT

cd "$TMPDIR"
git clone --depth 1 "https://github.com/$REPO.git" repo 2>/dev/null || {
    warn "No se pudo clonar el repo para iconos. Se omite instalación de .desktop"
    exit 0
}

cd repo

# Desktop file
sudo install -Dm644 data/novapm.desktop "$PREFIX/share/applications/novapm.desktop"
ok ".desktop instalado"

# Icons to hicolor
for dir in data/icons/hicolor/*/; do
    size=$(basename "$dir")
    sudo install -Dm644 "${dir}apps/novapm.png" "$PREFIX/share/icons/hicolor/$size/apps/novapm.png"
done
# ON/OFF at 256
sudo install -Dm644 data/icons/hicolor/256x256/apps/novapm-on.png \
    "$PREFIX/share/icons/hicolor/256x256/apps/novapm-on.png"
sudo install -Dm644 data/icons/hicolor/256x256/apps/novapm-off.png \
    "$PREFIX/share/icons/hicolor/256x256/apps/novapm-off.png"
# SVG
sudo install -Dm644 src/proxy_gui/icons/novapm.svg \
    "$PREFIX/share/icons/hicolor/scalable/apps/novapm.svg"
sudo install -Dm644 src/proxy_gui/icons/novapm-on.svg \
    "$PREFIX/share/icons/hicolor/scalable/apps/novapm-on.svg"
sudo install -Dm644 src/proxy_gui/icons/novapm-off.svg \
    "$PREFIX/share/icons/hicolor/scalable/apps/novapm-off.svg"
gtk-update-icon-cache -f /usr/share/icons/hicolor 2>/dev/null || true
ok "Iconos instalados"

# ---- Systemd service (optional) ----
echo ""
read -p "¿Instalar servicio systemd de usuario para novapm-local? [y/N] " -r
if [[ $REPLY =~ ^[Yy]$ ]]; then
    systemctl --user daemon-reload
    systemctl --user enable novapm-local.service
    systemctl --user start novapm-local.service
    ok "Servicio systemd instalado e iniciado"
    echo "  Para ver logs: journalctl --user -u novapm-local.service -f"
fi

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  NovaProxy Manager instalado correctamente${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "  Ejecutá:  novapm"
echo "  Ayuda:    novapm --help"
echo "  Wiki:     https://github.com/$REPO/wiki"
echo ""
