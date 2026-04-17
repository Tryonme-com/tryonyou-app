#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"

STAMP_C="@CertezaAbsoluta"
STAMP_L="@lo+erestu"
PATENT="PCT/EP2025/067317"
PROTOCOL="Bajo Protocolo de Soberania V10 - Founder: Ruben"
BOT_NAME="${TRYONYOU_DEPLOY_BOT_NAME:-@tryonyou_deploy_bot}"
DEPLOY_ZONE="${TRYONYOU_DEPLOY_ZONE:-Oberkampf (75011)}"

usage() {
  echo "Uso: ./supercommit_max.sh \"mensaje de commit\""
  echo
  echo "Opcional:"
  echo "  SUPERCOMMIT_RUN_BUILD=1   # ejecuta npm install + npm run build"
  echo "  SUPERCOMMIT_SKIP_NOTIFY=1 # omite notificacion Telegram"
  echo "  TELEGRAM_BOT_TOKEN / TELEGRAM_TOKEN + TELEGRAM_CHAT_ID"
}

if [[ "${1:-}" == "-h" || "${1:-}" == "--help" ]]; then
  usage
  exit 0
fi

BASE_MESSAGE="${1:-Supercommit Max sync bunker-galeria web}"
FULL_MESSAGE="$BASE_MESSAGE"
for required in "$STAMP_C" "$STAMP_L" "$PATENT" "$PROTOCOL"; do
  if [[ "$FULL_MESSAGE" != *"$required"* ]]; then
    FULL_MESSAGE="$FULL_MESSAGE $required"
  fi
done

current_branch="$(git rev-parse --abbrev-ref HEAD)"
if [[ "$current_branch" == "HEAD" ]]; then
  echo "ERROR: repositorio en detached HEAD."
  exit 1
fi

if [[ "${SUPERCOMMIT_RUN_BUILD:-0}" == "1" ]]; then
  echo "[Supercommit] Ejecutando build Vite..."
  npm install --no-fund --no-audit
  npm run build
fi

echo "[Supercommit] git add -A"
git add -A
if git diff --cached --quiet; then
  echo "[Supercommit] Sin cambios para commit."
else
  git commit -m "$FULL_MESSAGE"
fi

echo "[Supercommit] Push a rama: $current_branch"
git push -u origin "$current_branch"

resolve_chat_id() {
  local token="$1"
  local chat="${TRYONYOU_DEPLOY_CHAT_ID:-${TELEGRAM_CHAT_ID:-}}"
  if [[ -n "$chat" ]]; then
    echo "$chat"
    return 0
  fi
  chat="$(TOKEN="$token" python3 - <<'PY'
import json
import os
import urllib.request

token = os.environ.get("TOKEN", "").strip()
if not token:
    raise SystemExit(0)
url = f"https://api.telegram.org/bot{token}/getUpdates?limit=1&timeout=1"
try:
    with urllib.request.urlopen(url, timeout=10) as response:
        payload = json.loads(response.read().decode("utf-8"))
    results = payload.get("result") or []
    if not results:
        raise SystemExit(0)
    item = results[-1]
    message = item.get("message") or item.get("channel_post") or {}
    chat_id = (message.get("chat") or {}).get("id")
    if chat_id is not None:
        print(chat_id)
except Exception:
    pass
PY
)"
  echo "$chat"
}

send_telegram_success() {
  local token chat message api_url
  token="${TRYONYOU_DEPLOY_BOT_TOKEN:-${TELEGRAM_BOT_TOKEN:-${TELEGRAM_TOKEN:-}}}"
  token="${token//[[:space:]]/}"
  chat="$(resolve_chat_id "$token")"
  if [[ -z "$token" || -z "$chat" ]]; then
    echo "[Supercommit] Telegram omitido: faltan token o chat_id resoluble."
    return 0
  fi
  api_url="https://api.telegram.org/bot${token}/sendMessage"
  message="EXITO TRYONYOU
Bot: ${BOT_NAME}
Operacion: Supercommit_Max completado.
Sync: bunker ${DEPLOY_ZONE} con galeria web.
Rama: ${current_branch}
Sellos: ${STAMP_C} ${STAMP_L} ${PATENT}
${PROTOCOL}"
  curl -fsS -X POST "$api_url" \
    -d "chat_id=${chat}" \
    --data-urlencode "text=${message}" >/dev/null
  echo "[Supercommit] Notificacion enviada por Telegram."
}

if [[ "${SUPERCOMMIT_SKIP_NOTIFY:-0}" != "1" ]]; then
  send_telegram_success
fi

echo "[Supercommit] OK."