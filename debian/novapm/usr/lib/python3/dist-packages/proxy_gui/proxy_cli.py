"""CLI entry point for novapm — delegates to bash script or opens GUI."""

import sys
import os

from . import proxyctl


def main():
    proxyctl.ensure_files()
    script = str(proxyctl.PROXY_SCRIPT)

    if len(sys.argv) == 1:
        from .__main__ import main as gui_main
        gui_main()
        return

    cmd = sys.argv[1]
    if cmd == "uninstall":
        from .uninstall import run_uninstall
        run_uninstall()
        return

    if cmd == "update":
        from .update import run_update
        run_update()
        return

    os.execv(script, [script] + sys.argv[1:])
