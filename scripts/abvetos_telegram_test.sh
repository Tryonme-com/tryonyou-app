#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
if [[ -f "$ROOT/.env" ]]; then
  set -a
  # shellcheck disable=SC1091
  source "$ROOT/.env"
  set +a
fi
: "${TELEGRAM_BOT_TOKEN:?Defina TELEGRAM_BOT_TOKEN en .env}"
CHAT="${TELEGRAM_CHAT_ID:-7868120279}"
MSG="${1:-✅ BÚNKER CONECTADO. Escucha Activa Restaurada. ¡VÍVELO! BOOM. 💥}"
curl -sS -X POST "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage" \
  -d "chat_id=${CHAT}" \
  --data-urlencode "text=${MSG}" \
  -d "parse_mode=HTML"
echo
