#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT_DIR"

if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "❌ Este directorio no es un repositorio git."
  exit 1
fi

BRANCH_NAME="$(git rev-parse --abbrev-ref HEAD)"
if [[ "$BRANCH_NAME" == "HEAD" || -z "$BRANCH_NAME" ]]; then
  echo "❌ No hay rama activa para hacer push."
  exit 1
fi

BASE_MESSAGE="${1:-chore: Supercommit Max sincroniza búnker Oberkampf (75011) con galería web}"
REQUIRED_TAGS="@CertezaAbsoluta @lo+erestu PCT/EP2025/067317 Bajo Protocolo de Soberanía V10 - Founder: Rubén"
COMMIT_MESSAGE="${BASE_MESSAGE} ${REQUIRED_TAGS}"

echo "🏛️ SUPERCOMMIT MAX — rama: ${BRANCH_NAME}"
echo "🧱 Instalando dependencias y compilando frontend..."
npm install --no-fund --no-audit
npm run build

echo "🗂️ Preparando commit..."
git add -A
if git diff --cached --quiet; then
  echo "ℹ️ No hay cambios para commitear."
else
  git commit -m "$COMMIT_MESSAGE"
fi

echo "🚀 Sincronizando con origin/${BRANCH_NAME}..."
git push -u origin "$BRANCH_NAME"

send_telegram_signal() {
  local token_raw="${SUPERCOMMIT_TELEGRAM_TOKEN:-${TELEGRAM_BOT_TOKEN:-${TELEGRAM_TOKEN:-}}}"
  local token="${token_raw//[[:space:]]/}"
  local chat_id="${SUPERCOMMIT_TELEGRAM_CHAT_ID:-${TELEGRAM_CHAT_ID:-}}"

  if [[ -z "$token" ]]; then
    echo "ℹ️ Telegram no configurado (falta token)."
    return 0
  fi

  if [[ -z "$chat_id" ]]; then
    chat_id="$(SUPERCOMMIT_TOKEN="$token" python3 - <<'PY'
import os
import requests

token = os.environ["SUPERCOMMIT_TOKEN"]
url = f"https://api.telegram.org/bot{token}/getUpdates"
try:
    r = requests.get(url, timeout=30)
    r.raise_for_status()
    data = r.json()
    if not data.get("ok"):
        raise RuntimeError("getUpdates not ok")
    updates = data.get("result") or []
    for item in reversed(updates):
        msg = item.get("message") or item.get("channel_post") or {}
        chat = msg.get("chat") or {}
        chat_id = chat.get("id")
        if chat_id is not None:
            print(chat_id)
            raise SystemExit(0)
except Exception:
    pass
print("")
PY
)"
  fi

  if [[ -z "$chat_id" ]]; then
    echo "ℹ️ Telegram sin chat_id (define TELEGRAM_CHAT_ID o inicia chat con el bot)."
    return 0
  fi

  local text="✅ SUPERCOMMIT_MAX completado en ${BRANCH_NAME}. Búnker 75011 sincronizado con galería web."
  if ! SUPERCOMMIT_TOKEN="$token" SUPERCOMMIT_CHAT_ID="$chat_id" SUPERCOMMIT_TEXT="$text" \
    python3 - <<'PY'
import os
import requests

token = os.environ["SUPERCOMMIT_TOKEN"]
chat_id = os.environ["SUPERCOMMIT_CHAT_ID"]
text = os.environ["SUPERCOMMIT_TEXT"]
url = f"https://api.telegram.org/bot{token}/sendMessage"
payload = {"chat_id": chat_id, "text": text}
try:
    r = requests.post(url, json=payload, timeout=30)
    r.raise_for_status()
    print("📣 Notificación Telegram enviada.")
except Exception as exc:
    print(f"⚠️ Notificación Telegram no entregada: {exc}")
PY
  then
    echo "⚠️ Fallo en notificación Telegram (no bloqueante)."
  fi
}

send_telegram_signal
echo "🎯 Supercommit Max finalizado."