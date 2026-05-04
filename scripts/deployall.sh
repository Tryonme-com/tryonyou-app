#!/usr/bin/env bash
set -euo pipefail

DRY=false
if [[ "${1:-}" == "--dry" ]]; then
  DRY=true
elif [[ $# -gt 0 ]]; then
  echo "[deployall] Flag no reconocida: $1" >&2
  exit 2
fi

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

if [[ "$DRY" == "true" ]]; then
  echo "[deployall] Dry run OK: deployall disponible."
  exit 0
fi

if [[ -z "${VERCEL_TOKEN:-}" ]]; then
  echo "[deployall] VERCEL_TOKEN no definido; despliegue cancelado." >&2
  exit 3
fi

if ! command -v vercel >/dev/null 2>&1; then
  echo "[deployall] Vercel CLI no disponible en PATH; instala dependencias antes de desplegar." >&2
  exit 127
fi

vercel deploy --prod --yes --token="$VERCEL_TOKEN"
