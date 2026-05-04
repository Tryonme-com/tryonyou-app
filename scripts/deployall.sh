#!/usr/bin/env bash
set -euo pipefail

DRY_RUN=false

for arg in "$@"; do
  case "$arg" in
    --dry) DRY_RUN=true ;;
    *)
      echo "[deployall] Flag no reconocida: $arg" >&2
      exit 2
      ;;
  esac
done

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

echo "[deployall] Tests Python."
python3 -m unittest discover -s tests -p 'test_*.py' -v

echo "[deployall] Typecheck TypeScript."
npx tsc --noEmit

echo "[deployall] Build Vite."
npm run build

if [[ "$DRY_RUN" == "true" ]]; then
  echo "[deployall] Dry-run completado: sin despliegue."
  exit 0
fi

if [[ -z "${VERCEL_TOKEN:-}" ]]; then
  echo "[deployall] VERCEL_TOKEN ausente: validación completada sin despliegue."
  exit 0
fi

echo "[deployall] Vercel production build/deploy."
vercel pull --yes --environment=production --token="$VERCEL_TOKEN"
vercel build --prod --token="$VERCEL_TOKEN"
vercel deploy --prebuilt --prod --token="$VERCEL_TOKEN"
