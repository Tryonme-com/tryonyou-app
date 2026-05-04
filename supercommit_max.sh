#!/usr/bin/env bash
set -euo pipefail

FAST=false
DEPLOY=false
BRANCH="$(git branch --show-current)"

if [[ -z "$BRANCH" ]]; then
  echo "[supercommit_max] No hay rama git activa; abortando." >&2
  exit 2
fi

for arg in "$@"; do
  case "$arg" in
    --fast) FAST=true ;;
    --deploy) DEPLOY=true ;;
    *)
      echo "[supercommit_max] Flag no reconocida: $arg" >&2
      exit 2
      ;;
  esac
done

if [[ "$FAST" != "true" ]]; then
  echo "[supercommit_max] Typecheck y build."
  npm run typecheck
  npm run build
fi

if [[ -z "$(git status --porcelain)" ]]; then
  echo "[supercommit_max] Nada que commitear."
  exit 0
fi

git add -A

git commit -m "$(cat <<'EOF'
chore(supercommit): sincronizar bunker Oberkampf con galeria web

@CertezaAbsoluta @lo+erestu PCT/EP2025/067317 - Bajo Protocolo de Soberania V10 - Founder: Ruben
EOF
)"

git push -u origin "$BRANCH"

if [[ "$DEPLOY" == "true" ]]; then
  echo "[supercommit_max] deployall (puede desplegar si hay VERCEL_TOKEN)."
  npm run deployall
fi