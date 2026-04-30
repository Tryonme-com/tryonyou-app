#!/usr/bin/env bash
set -euo pipefail

FAST=false
DEPLOY=false

for arg in "${@:-}"; do
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
fix(merge): resolver conflictos y restaurar typecheck

@CertezaAbsoluta @lo+erestu PCT/EP2025/067317 — Bajo Protocolo de Soberanía V10 - Founder: Rubén
EOF
)"

if [[ "$DEPLOY" == "true" ]]; then
  echo "[supercommit_max] deployall (puede desplegar si hay VERCEL_TOKEN)."
  npm run deployall
fi