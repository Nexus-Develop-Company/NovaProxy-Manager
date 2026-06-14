"""System notifications for proxy state changes."""

import subprocess
from pathlib import Path

ICON_DIR = Path(__file__).parent / "icons"


def notify(title: str, message: str, icon: str = "proxy-on") -> None:
    """Send a desktop notification via notify-send."""
    icon_path = ICON_DIR / f"{icon}.svg"
    cmd = ["notify-send", title, message]
    if icon_path.exists():
        cmd.extend(["--icon", str(icon_path)])
    try:
        subprocess.run(cmd, capture_output=True, timeout=5)
    except Exception:
        pass
