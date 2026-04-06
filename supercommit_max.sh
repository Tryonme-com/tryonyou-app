#!/usr/bin/env bash
# Supercommit máximo: add, commit con sellos TryOnYou, push.
#
# Mensaje opcional: $1 debe contener @CertezaAbsoluta, @lo+erestu y PCT/EP2025/067317
# (si falta alguno, el script sale con error 1 antes de git add).
#
# Push solo si:
#   1) En esta ejecución se hizo un commit nuevo, o
#   2) No hubo nada que commitear pero la rama local tiene commits sin publicar
#      respecto a @{u} (evita quedar desincronizado tras commits previos).
# Si no hay upstream configurado, no se hace push (evita errores en CI).
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"

MSG="${1:-Protocolo Soberanía V10: mirror + Pau Marais + Firebase applet @CertezaAbsoluta @lo+erestu PCT/EP2025/067317 Bajo Protocolo de Soberanía V10 - Founder: Rubén}"

# Regla TryOnYou: sellos + protocolo Stirpe Lafayette.
_commit_stamps_ok() {
  local m="$1"
  [[ "$m" == *"@CertezaAbsoluta"* ]] || { echo "❌ Falta @CertezaAbsoluta en el mensaje de commit." >&2; return 1; }
  [[ "$m" == *"@lo+erestu"* ]] || { echo "❌ Falta @lo+erestu en el mensaje de commit." >&2; return 1; }
  [[ "$m" == *"PCT/EP2025/067317"* ]] || { echo "❌ Falta la patente PCT/EP2025/067317 en el mensaje de commit." >&2; return 1; }
  [[ "$m" == *"Bajo Protocolo de Soberanía V10"* ]] || { echo "❌ Falta «Bajo Protocolo de Soberanía V10» en el mensaje de commit." >&2; return 1; }
  [[ "$m" == *"Founder: Rubén"* ]] || { echo "❌ Falta «Founder: Rubén» en el mensaje de commit." >&2; return 1; }
  return 0
}
if ! _commit_stamps_ok "$MSG"; then
  echo "   Uso: $0 'Tu título @CertezaAbsoluta @lo+erestu PCT/EP2025/067317 Bajo Protocolo de Soberanía V10 - Founder: Rubén'" >&2
  exit 1
fi

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
