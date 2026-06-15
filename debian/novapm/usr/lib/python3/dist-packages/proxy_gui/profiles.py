"""Profile manager — stores and switches proxy profiles."""

import json
from pathlib import Path

from . import proxyctl

PROFILES_FILE = Path.home() / ".config" / "proxy" / "profiles.json"


class ProfileManager:
    def __init__(self):
        self._data = self._load()

    def _load(self):
        if PROFILES_FILE.exists():
            try:
                return json.loads(PROFILES_FILE.read_text())
            except (json.JSONDecodeError, KeyError):
                pass
        return {"active": None, "profiles": {}}

    def _save(self):
        PROFILES_FILE.parent.mkdir(parents=True, exist_ok=True)
        PROFILES_FILE.write_text(json.dumps(self._data, indent=2))

    def list(self):
        return sorted(self._data["profiles"].keys())

    def get(self, name):
        return dict(self._data["profiles"].get(name, {}))

    def save(self, name, config):
        self._data["profiles"][name] = config
        self._save()

    def delete(self, name):
        if name == self._data.get("active"):
            return False
        self._data["profiles"].pop(name, None)
        self._save()
        return True

    def current(self):
        return self._data.get("active")

    def switch(self, name):
        if name not in self._data["profiles"]:
            return False, "Perfil no encontrado"
        config = self._data["profiles"][name]
        self._data["active"] = name
        self._save()
        proxyctl.write_config(config)
        success, output = proxyctl.run_proxy("apply")
        return success, output

    def exists(self, name):
        return name in self._data["profiles"]

    def is_active(self, name):
        return name == self._data.get("active")

    def set_active(self, name):
        if name in self._data["profiles"]:
            self._data["active"] = name
            self._save()
