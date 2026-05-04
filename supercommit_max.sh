#!/usr/bin/env bash
set -euo pipefail

FAST=false
DEPLOY=false
MESSAGE="chore: sincronizar bunker Oberkampf con galeria web"
REQUIRED_STAMP="@CertezaAbsoluta @lo+erestu PCT/EP2025/067317"
SOVEREIGN_STAMP="Bajo Protocolo de Soberanía V10 - Founder: Rubén"

usage() {
  cat <<'EOF'
Uso: bash supercommit_max.sh [--fast] [--deploy] [--msg "mensaje"]

Opciones:
  --fast          Omite npm run typecheck/build.
  --deploy        Ejecuta npm run deployall tras commit/push.
  --msg MESSAGE   Mensaje base del commit; los sellos obligatorios se anexan.
EOF
}

notify_success() {
  local text="$1"
  local token chat response chat_from_update

  token="${TRYONYOU_DEPLOY_BOT_TOKEN:-${TELEGRAM_BOT_TOKEN:-${TELEGRAM_TOKEN:-}}}"
  chat="${TRYONYOU_DEPLOY_CHAT_ID:-${TELEGRAM_CHAT_ID:-}}"

  if [[ -z "$token" ]]; then
    echo "[supercommit_max] Notificacion omitida: falta TRYONYOU_DEPLOY_BOT_TOKEN/TELEGRAM_BOT_TOKEN."
    return 0
  fi
  if ! command -v curl >/dev/null 2>&1; then
    echo "[supercommit_max] Notificacion omitida: curl no disponible."
    return 0
  fi

  if [[ -z "$chat" ]]; then
    response="$(curl -fsS "https://api.telegram.org/bot${token}/getUpdates" 2>/dev/null || true)"
    chat_from_update="$(printf '%s' "$response" | python3 -c 'import json,sys
try:
    data=json.load(sys.stdin)
    updates=data.get("result") or []
    for item in reversed(updates):
        chat=(item.get("message") or item.get("channel_post") or {}).get("chat") or {}
        if chat.get("id") is not None:
            print(chat["id"])
            break
except Exception:
    pass
' 2>/dev/null || true)"
    chat="$chat_from_update"
  fi

  if [[ -z "$chat" ]]; then
    echo "[supercommit_max] Notificacion omitida: falta TRYONYOU_DEPLOY_CHAT_ID/TELEGRAM_CHAT_ID."
    return 0
  fi

  curl -fsS -X POST "https://api.telegram.org/bot${token}/sendMessage" \
    -d "chat_id=${chat}" \
    --data-urlencode "text=@tryonyou_deploy_bot ${text}" >/dev/null \
    || echo "[supercommit_max] Aviso: Telegram no confirmo la notificacion."
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --fast)
      FAST=true
      shift
      ;;
    --deploy)
      DEPLOY=true
      shift
      ;;
    --msg)
      if [[ $# -lt 2 || -z "${2:-}" ]]; then
        echo "[supercommit_max] --msg requiere un valor." >&2
        exit 2
      fi
      MESSAGE="$2"
      shift 2
      ;;
    --msg=*)
      MESSAGE="${1#--msg=}"
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "[supercommit_max] Flag no reconocida: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
done

if [[ "$MESSAGE" != *"$REQUIRED_STAMP"* ]]; then
  MESSAGE="${MESSAGE} ${REQUIRED_STAMP}"
fi
if [[ "$MESSAGE" != *"$SOVEREIGN_STAMP"* ]]; then
  MESSAGE="${MESSAGE} ${SOVEREIGN_STAMP}"
fi

if [[ "$FAST" != "true" ]]; then
  echo "[supercommit_max] Typecheck y build."
  npm run typecheck
  npm run build
fi

if [[ -z "$(git status --porcelain)" ]]; then
  echo "[supercommit_max] Nada que commitear."
  notify_success "Supercommit_Max sin cambios; bunker Oberkampf 75011 y galeria web ya sincronizados."
  exit 0
fi

git add -A
git reset -q -- .env .env.* logs '*.pem' '*.key' '*.p12' '*.pfx' '*.crt' 2>/dev/null || true

if git diff --cached --quiet; then
  echo "[supercommit_max] No hay cambios seguros para commitear tras excluir secretos/runtime."
  notify_success "Supercommit_Max sin cambios seguros para publicar."
  exit 0
fi

git commit -m "$MESSAGE"

branch="$(git branch --show-current)"
if [[ -z "$branch" ]]; then
  echo "[supercommit_max] No se pudo determinar la rama actual." >&2
  exit 1
fi

git push -u origin "$branch"

if [[ "$DEPLOY" == "true" ]]; then
  echo "[supercommit_max] deployall (puede desplegar si hay VERCEL_TOKEN)."
  npm run deployall
fi

notify_success "Supercommit_Max completado en ${branch}: bunker Oberkampf 75011 sincronizado con galeria web."