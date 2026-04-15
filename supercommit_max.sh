#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"

COMMIT_MSG="${1:-}"
if [[ -z "$COMMIT_MSG" ]]; then
  COMMIT_MSG="SUPERCOMMIT_MAX: sincronización búnker Oberkampf 75011 + galería web @CertezaAbsoluta @lo+erestu PCT/EP2025/067317 Bajo Protocolo de Soberanía V10 - Founder: Rubén"
fi

BOT_TOKEN="${TRYONYOU_DEPLOY_BOT_TOKEN:-${TELEGRAM_BOT_TOKEN:-${TELEGRAM_TOKEN:-}}}"
CHAT_ID="${TRYONYOU_DEPLOY_CHAT_ID:-${TELEGRAM_CHAT_ID:-}}"
BRANCH="$(git rev-parse --abbrev-ref HEAD)"

autodetect_chat_id() {
  if [[ -n "$CHAT_ID" || -z "$BOT_TOKEN" ]]; then
    return 0
  fi
  local updates raw id
  updates="$(curl -fsS --max-time 20 "https://api.telegram.org/bot${BOT_TOKEN}/getUpdates" || true)"
  if [[ -z "$updates" ]]; then
    return 0
  fi
  id="$(printf '%s' "$updates" | python3 -c 'import json,sys
try:
  data=json.load(sys.stdin)
  updates=data.get("result",[])
  for item in reversed(updates):
    msg=item.get("message") or item.get("channel_post") or {}
    chat=msg.get("chat") or {}
    cid=chat.get("id")
    if cid is not None:
      print(cid); break
except Exception:
  pass
')"
  if [[ -n "$id" ]]; then
    CHAT_ID="$id"
    echo "ℹ️ Chat ID autodetectado desde getUpdates."
  fi
}

notify_success() {
  local step="$1"
  if [[ -z "$BOT_TOKEN" || -z "$CHAT_ID" ]]; then
    echo "ℹ️ Notificación omitida (faltan token/chat_id en entorno). Paso: $step"
    return 0
  fi
  local text
  text="✅ @tryonyou_deploy_bot | ${step}%0ABranch: ${BRANCH}%0APatente: PCT/EP2025/067317"
  curl -fsS --max-time 20 \
    -X POST "https://api.telegram.org/bot${BOT_TOKEN}/sendMessage" \
    -d "chat_id=${CHAT_ID}" \
    -d "text=${text}" >/dev/null
  echo "📡 Notificación enviada: $step"
}

echo "🏛️ SUPERCOMMIT_MAX: build + sync + git en rama actual ($BRANCH)"
autodetect_chat_id

npm install --no-fund --no-audit
notify_success "Dependencias instaladas"

npm run build
notify_success "Build Vite sin errores Bash"

if [[ -f "$ROOT/sincronizar_bunker_total_safe.py" ]]; then
  E50_PROJECT_ROOT="$ROOT" E50_GIT_PUSH=0 python3 "$ROOT/sincronizar_bunker_total_safe.py"
  notify_success "Sincronización búnker Oberkampf 75011 con galería web"
fi

git add -A -- . \
  ':!.env' \
  ':!.env.*' \
  ':!*.pem' \
  ':!*.key' \
  ':!*.p12' \
  ':!*.pfx' \
  ':!*.crt'
if git diff --cached --quiet; then
  echo "ℹ️ Sin cambios para commit."
else
  git commit -m "$COMMIT_MSG"
  notify_success "Commit creado"
fi

git push -u origin "$BRANCH"
notify_success "Push completado"

echo "✅ SUPERCOMMIT_MAX completado."