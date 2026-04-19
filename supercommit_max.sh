#!/usr/bin/env bash
# Supercommit máximo: add + commit sellado + push opcional + deploy opcional.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"

FAST=0
DEPLOY=0
CUSTOM_MSG=""

usage() {
  cat <<'USAGE'
Uso:
  bash supercommit_max.sh [--fast] [--deploy] [--msg "mensaje custom"]

Opciones:
  --fast      Omite build/tests antes del commit.
  --deploy    Requiere VERCEL_TOKEN y ejecuta deploy prod.
  --msg       Mensaje base de commit (los sellos se autoañaden si faltan).
USAGE
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --fast)
      FAST=1
      shift
      ;;
    --deploy)
      DEPLOY=1
      shift
      ;;
    --msg)
      shift
      if [[ $# -eq 0 ]]; then
        echo "❌ --msg requiere un valor." >&2
        exit 1
      fi
      CUSTOM_MSG="$1"
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      # Retrocompatibilidad: permitir mensaje posicional.
      if [[ -z "$CUSTOM_MSG" ]]; then
        CUSTOM_MSG="$1"
      else
        CUSTOM_MSG="$CUSTOM_MSG $1"
      fi
      shift
      ;;
  esac
done

DEFAULT_MSG="OMEGA_DEPLOY: sincronización bunker Oberkampf 75011 + galería web"
MSG="${CUSTOM_MSG:-$DEFAULT_MSG}"

_append_if_missing() {
  local input="$1"
  local token="$2"
  if [[ "$input" != *"$token"* ]]; then
    input="$input $token"
  fi
  printf '%s' "$input"
}

# Regla TryOnYou: todo commit debe llevar sellos + protocolo fundador.
MSG="$(_append_if_missing "$MSG" "@CertezaAbsoluta")"
MSG="$(_append_if_missing "$MSG" "@lo+erestu")"
MSG="$(_append_if_missing "$MSG" "PCT/EP2025/067317")"
MSG="$(_append_if_missing "$MSG" "Bajo Protocolo de Soberanía V10 - Founder: Rubén")"

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
  exit 1
fi

if [[ "$FAST" -eq 0 ]]; then
  echo "▶ Vite production build"
  npm run build
  echo "▶ Python tests"
  python3 -m unittest tests/test_supercommit_max.py
fi

git add -A
did_commit=0
if git diff --cached --quiet; then
  echo "Nada nuevo en el índice tras git add (sin commit en esta pasada)."
else
  git commit -m "$MSG"
  did_commit=1
fi

if [[ "$did_commit" -eq 1 ]]; then
  echo "Commit creado: git push."
  git push
elif git rev-parse --verify "@{u}" >/dev/null 2>&1; then
  ahead="$(git rev-list --count "@{u}..HEAD" 2>/dev/null || true)"
  ahead="${ahead:-0}"
  case "$ahead" in
    *[!0-9]*) ahead=0 ;;
  esac
  if [[ "$ahead" -gt 0 ]]; then
    echo "Sin commit nuevo, pero la rama va ${ahead} commit(s) por delante del remoto: git push."
    git push
  else
    echo "Sin push: índice sin cambios y la rama no está por delante del remoto."
  fi
else
  echo "Sin push: no hay upstream (@{u}). Configura tracking (git push -u) o empuja a mano."
fi

if [[ "$DEPLOY" -eq 1 ]]; then
  if [[ -z "${VERCEL_TOKEN:-}" ]]; then
    echo "❌ --deploy requiere VERCEL_TOKEN en el entorno." >&2
    exit 1
  fi
  echo "▶ Deploy Vercel (prod)"
  vercel deploy --prod --yes --token "$VERCEL_TOKEN"
fi