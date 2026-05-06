#!/usr/bin/env bash
set -euo pipefail

DRY=false
if [[ "${1:-}" == "--dry" ]]; then
  DRY=true
fi

echo "[deployall] Validacion bunker/galeria."
npm install --no-fund --no-audit
python3 -m unittest discover -s tests -p 'test_*.py'
npm run typecheck
npm run build

if [[ "$DRY" == "true" ]]; then
  echo "[deployall] Dry run completado; despliegue omitido."
  exit 0
fi

if [[ -z "${VERCEL_TOKEN:-}" ]]; then
  echo "[deployall] VERCEL_TOKEN ausente; despliegue omitido tras validacion local."
  exit 0
fi

vercel deploy --prod --yes --token="$VERCEL_TOKEN"
