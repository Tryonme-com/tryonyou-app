#!/usr/bin/env bash
# Local/CI parity for TryOnYou gallery validation and optional Vercel deploy.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

DRY_RUN=false

for arg in "$@"; do
  case "$arg" in
    --dry) DRY_RUN=true ;;
    -h|--help)
      echo "Uso: bash scripts/deployall.sh [--dry]"
      exit 0
      ;;
    *)
      echo "[deployall] Flag no reconocida: $arg" >&2
      exit 2
      ;;
  esac
done

if [[ -f package-lock.json ]]; then
  npm ci --no-audit --no-fund
else
  npm install --no-audit --no-fund
fi

python3 -m unittest discover -s tests -p 'test_*.py' -v
npm run typecheck
npm run build

if [[ "$DRY_RUN" == "true" ]]; then
  echo "[deployall] Dry run OK; despliegue omitido."
  exit 0
fi

if [[ -z "${VERCEL_TOKEN:-}" ]]; then
  echo "[deployall] VERCEL_TOKEN ausente; validacion completada sin despliegue."
  exit 0
fi

if ! command -v vercel >/dev/null 2>&1; then
  echo "[deployall] Vercel CLI ausente; instala vercel o usa CI para desplegar." >&2
  exit 1
fi

vercel pull --yes --environment=production --token "$VERCEL_TOKEN"
vercel build --prod --token "$VERCEL_TOKEN"
vercel deploy --prebuilt --prod --token "$VERCEL_TOKEN"
