#!/usr/bin/env bash
# TryOnMe Voice — instalación, comprobación .env y Uvicorn :8000
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"

if [[ ! -f .env ]]; then
  echo "Falta .env. Copia .env.example a .env y rellena GEMINI_API_KEY." >&2
  exit 1
fi

python3 - <<'PY'
from pathlib import Path
p = Path(".env")
keys = {}
for line in p.read_text(encoding="utf-8").splitlines():
    line = line.strip()
    if not line or line.startswith("#") or "=" not in line:
        continue
    k, _, v = line.partition("=")
    keys[k.strip()] = v.strip().strip('"').strip("'")
if not any((keys.get(k) or "").strip() for k in ("GEMINI_API_KEY", "GOOGLE_API_KEY")):
    raise SystemExit("En .env debe existir GEMINI_API_KEY o GOOGLE_API_KEY con valor no vacío.")
PY

if [[ ! -d .venv ]]; then
  python3 -m venv .venv
fi
# shellcheck source=/dev/null
source .venv/bin/activate
pip install -r requirements.txt

export VOICE_AGENT_PORT="${VOICE_AGENT_PORT:-8000}"
exec "$ROOT/.venv/bin/uvicorn" main:app --host 0.0.0.0 --port "$VOICE_AGENT_PORT"
