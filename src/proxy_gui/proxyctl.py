"""Proxy control module — reads/writes config, executes proxy script."""

import os
import subprocess
import stat
import configparser
from pathlib import Path

CONFIG_DIR = Path.home() / ".config" / "proxy"
CONFIG_FILE = CONFIG_DIR / "proxy.conf"
ENV_FILE = CONFIG_DIR / "env.zsh"
PROXY_SCRIPT = Path.home() / ".local" / "bin" / "novapm-bash"
PROXY_LOCAL = Path.home() / ".local" / "bin" / "novapm-local.py"
ASKPASS = Path.home() / ".local" / "bin" / "proxy-askpass"
SYSTEMD_USER_DIR = Path.home() / ".config" / "systemd" / "user"
SERVICE_FILE = SYSTEMD_USER_DIR / "novapm-local.service"
LOCAL_BIN = Path.home() / ".local" / "bin"

DEFAULT_CONFIG = """# ==========================================
# Configuración única de proxy
# Edita solo este archivo cuando cambien
# las credenciales o el servidor proxy.
# ==========================================

# Proxy local (novapm-local.py escucha aquí — sin autenticación)
PROXY_HOST="127.0.0.1"
PROXY_PORT="3128"

# Proxy corporativo upstream (proxy-local.py se conecta con Basic auth)
UPSTREAM_HOST="10.12.0.205"
UPSTREAM_PORT="3128"
UPSTREAM_USER=""
UPSTREAM_PASS=""

# Dominios que NO usan proxy (separados por coma)
NO_PROXY="localhost,127.0.0.1,::1,10.0.0.0/8,172.16.0.0/12,192.168.0.0/16,*.local"
"""


def _copy_data(name: str, dest: Path, executable: bool = False):
    """Copy an embedded data file to dest."""
    import importlib.resources as res
    data = res.read_binary("proxy_gui.data", name)
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(data)
    if executable:
        dest.chmod(dest.stat().st_mode | stat.S_IEXEC | stat.S_IXGRP | stat.S_IXOTH)


def ensure_files():
    """Extract embedded data files (always overwrite scripts, preserve config)."""
    _copy_data("novapm-bash", PROXY_SCRIPT, executable=True)
    _copy_data("novapm-local.py", PROXY_LOCAL, executable=True)
    _copy_data("novapm-local.service", SERVICE_FILE)
    _copy_data("askpass.py", ASKPASS, executable=True)

    if not CONFIG_FILE.exists():
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        CONFIG_FILE.write_text(DEFAULT_CONFIG)

    subprocess.run(
        ["systemctl", "--user", "daemon-reload"],
        capture_output=True, timeout=10,
    )


def parse_config() -> dict:
    """Read proxy.conf and return a dict of values."""
    cfg = {}
    if not CONFIG_FILE.exists():
        return cfg
    for line in CONFIG_FILE.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        cfg[key.strip()] = value.strip().strip('"').strip("'")
    return cfg


def write_config(values: dict) -> None:
    """Write proxy.conf from a dict of values."""
    lines = [
        "# ==========================================",
        "# Configuración única de proxy",
        "# Editado desde NovaProxy Manager",
        "# ==========================================",
        "",
        "# Proxy local (fijo — no editable)",
        'PROXY_HOST="127.0.0.1"',
        'PROXY_PORT="3128"',
        "",
        "# Proxy corporativo upstream",
        f'UPSTREAM_HOST="{values.get("UPSTREAM_HOST", "10.12.0.205")}"',
        f'UPSTREAM_PORT="{values.get("UPSTREAM_PORT", "3128")}"',
        f'UPSTREAM_USER="{values.get("UPSTREAM_USER", "")}"',
        f'UPSTREAM_PASS="{values.get("UPSTREAM_PASS", "")}"',
        "",
        "# Dominios que NO usan proxy",
        f'NO_PROXY="{values.get("NO_PROXY", "")}"',
        "",
    ]
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    CONFIG_FILE.write_text("\n".join(lines) + "\n")


def run_proxy(command: str) -> tuple[bool, str]:
    """Run proxy on/off/auto/status and return (success, output)."""
    if not PROXY_SCRIPT.exists():
        return False, f"Script not found: {PROXY_SCRIPT}"

    env = os.environ.copy()
    if ASKPASS.exists():
        env["SUDO_ASKPASS"] = str(ASKPASS)

    try:
        result = subprocess.run(
            [str(PROXY_SCRIPT), command],
            capture_output=True, text=True, timeout=30,
            env=env,
        )
        return result.returncode == 0, result.stdout + result.stderr
    except subprocess.TimeoutExpired:
        return False, "Command timed out"
    except Exception as e:
        return False, str(e)


def is_proxy_local_running() -> bool:
    """Check if proxy-local.py process is running."""
    try:
        result = subprocess.run(
            ["pgrep", "-f", "novapm-local.py"],
            capture_output=True, timeout=5,
        )
        return result.returncode == 0
    except Exception:
        return False


def get_shell_env() -> str | None:
    """Read http_proxy from env.zsh if it exists."""
    if not ENV_FILE.exists():
        return None
    for line in ENV_FILE.read_text().splitlines():
        if line.startswith("export http_proxy="):
            return line.split("=", 1)[1].strip().strip('"')
    return None


def get_status() -> dict:
    """Return dict with status of all proxy components."""
    env = get_shell_env()
    return {
        "proxy_local": is_proxy_local_running(),
        "env_var": env,
        "api": bool(env),
        "script_exists": PROXY_SCRIPT.exists(),
        "config_exists": CONFIG_FILE.exists(),
    }
