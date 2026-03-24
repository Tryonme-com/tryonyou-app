#!/usr/bin/env bash
# Supercommit máximo: add, commit con sellos TryOnYou, push.
#
# Push solo si:
#   1) En esta ejecución se hizo un commit nuevo, o
#   2) No hubo nada que commitear pero la rama local tiene commits sin publicar
#      respecto a @{u} (evita quedar desincronizado tras commits previos).
# Si no hay upstream configurado, no se hace push (evita errores en CI).
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"

MSG="${1:-Protocolo Soberanía: mirror V10 sello Divineo + fallback CSS @CertezaAbsoluta @lo+erestu PCT/EP2025/067317}"

git add -A
did_commit=0
if git diff --cached --quiet; then
  echo "Nada nuevo en el índice tras git add (sin commit en esta pasada)."
else
  git commit -m "$MSG"
  did_commit=1
fi

if [ "$did_commit" -eq 1 ]; then
  echo "Commit creado: git push."
  git push
elif git rev-parse --verify "@{u}" >/dev/null 2>&1; then
  ahead="$(git rev-list --count "@{u}..HEAD" 2>/dev/null || true)"
  ahead="${ahead:-0}"
  case "$ahead" in
    *[!0-9]*) ahead=0 ;;
  esac
  if [ "$ahead" -gt 0 ]; then
    echo "Sin commit nuevo, pero la rama va ${ahead} commit(s) por delante del remoto: git push."
    git push
  else
    echo "Sin push: índice sin cambios y la rama no está por delante del remoto."
  fi
else
  echo "Sin push: no hay upstream (@{u}). Configura tracking (git push -u) o empuja a mano."
fi
