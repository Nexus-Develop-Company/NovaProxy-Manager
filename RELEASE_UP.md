# RELEASE UP — NovaProxy Manager

Guía para publicar una nueva versión de NovaProxy Manager.

---

## 1. Bump de versión

Actualizar `version` en:

| Archivo | Dónde |
|---------|-------|
| `pyproject.toml` | `version = "X.Y.Z"` |
| `Makefile` | `VERSION = X.Y.Z` |
| `src/proxy_gui/__init__.py` | `__version__ = "X.Y.Z"` |
| `src/proxy_gui/manual.py` | Texto al final: `NovaProxy Manager vX.Y.Z` |
| `debian/changelog` | Nuevo entry con la versión |

## 2. Changelog

Agregar entry en `debian/changelog`:

```
novapm (X.Y.Z-1) unstable; urgency=medium

  * Descripción de cambios.

 -- Nexus Develop Company <marcosjaviersantana300302@gmail.com>  $(date +"%a, %d %b %Y %H:%M:%S %z")
```

## 3. Commit + Tag

```bash
git add -A
git commit -m "Version X.Y.Z"
git tag -a vX.Y.Z -m "Version X.Y.Z"
git push && git push --tags
```

## 4. Compilar .deb

```bash
make clean
make deb
```

Esto genera `../novapm_X.Y.Z-1_all.deb`.

## 5. Actualizar APT repo

```bash
# Configurar gh-pages (solo primera vez)
git worktree add /tmp/gh-pages gh-pages

# Copiar .deb
cp ../novapm_X.Y.Z-1_all.deb /tmp/gh-pages/apt/pool/main/n/novapm/

# Regenerar Packages
cd /tmp/gh-pages/apt
dpkg-scanpackages --multiversion . > /dev/null 2>&1
dpkg-scanpackages . /dev/null | gzip -9c > dists/stable/main/binary-all/Packages.gz

# Firmar Release
cd /tmp/gh-pages/apt/dists/stable
cat > Release << EOF
Origin: NovaProxy Manager
Label: NovaProxy Manager APT Repository
Suite: stable
Codename: stable
Architectures: all
Components: main
Description: APT repository for NovaProxy Manager
Date: $(date -Ru)
$(apt-ftparchive release .)
EOF
gpg --default-key "Nexus Develop Company" -abs -o Release.gpg Release
gpg --default-key "Nexus Develop Company" --clearsign -o InRelease Release

# Commit y push
cd /tmp/gh-pages
git add -A
git commit -m "Release X.Y.Z: update APT repo"
git push origin gh-pages
```

## 6. GitHub Release

```bash
gh release create vX.Y.Z \
  --title "NovaProxy Manager vX.Y.Z" \
  --notes "Ver changelog en debian/changelog" \
  ../novapm_X.Y.Z-1_all.deb
```

---

## Checklist pre-release

- [ ] Versión bump en todos los archivos
- [ ] Changelog actualizado
- [ ] Código probado (`novapm on/off/status`)
- [ ] Iconos regenerados si cambió el SVG
- [ ] .deb compila sin errores
- [ ] APT repo actualizado
- [ ] Tag y release creados
