#!/usr/bin/env bash
# supercommit_max — sincronización búnker/galería con sellos soberanos.
#
# Uso:
#   ./supercommit_max.sh "mensaje opcional"
#
# Variables:
#   SUPERCOMMIT_SKIP_BUILD=1   # omite npm install + npm run build
#   SUPERCOMMIT_SKIP_PUSH=1    # omite git push
#   SUPERCOMMIT_DEPLOY=1       # despliegue Vercel (requiere VERCEL_TOKEN y vercel CLI)
#   TRYONYOU_DEPLOY_BOT_TOKEN  # token bot Telegram (o TELEGRAM_BOT_TOKEN / TELEGRAM_TOKEN)
#   TRYONYOU_DEPLOY_BOT_CHAT_ID# chat objetivo (o TELEGRAM_CHAT_ID)
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"

default_msg="chore: Supercommit_Max sincroniza búnker Oberkampf (75011) con galería web @CertezaAbsoluta @lo+erestu PCT/EP2025/067317 Bajo Protocolo de Soberanía V10 - Founder: Rubén"
commit_msg="${1:-$default_msg}"

ensure_marker() {
  local marker="$1"
  if [[ "$commit_msg" != *"$marker"* ]]; then
    commit_msg="$commit_msg $marker"
  fi
}

ensure_marker "@CertezaAbsoluta"
ensure_marker "@lo+erestu"
ensure_marker "PCT/EP2025/067317"
ensure_marker "Bajo Protocolo de Soberanía V10 - Founder: Rubén"

branch="$(git rev-parse --abbrev-ref HEAD)"
if [[ "$branch" == "HEAD" ]]; then
  echo "❌ Repositorio en detached HEAD; abortando." >&2
  exit 2
fi

notify_telegram() {
  local text="$1"
  local token="${TRYONYOU_DEPLOY_BOT_TOKEN:-${TELEGRAM_BOT_TOKEN:-${TELEGRAM_TOKEN:-}}}"
  local chat="${TRYONYOU_DEPLOY_BOT_CHAT_ID:-${TELEGRAM_CHAT_ID:-}}"
  token="$(echo -n "$token" | tr -d '[:space:]')"
  chat="$(echo -n "$chat" | tr -d '[:space:]')"

  if [[ -z "$token" || -z "$chat" ]]; then
    echo "ℹ️ Notificación Telegram omitida (token/chat_id no configurados)."
    return 0
  fi

  curl -sS -X POST "https://api.telegram.org/bot${token}/sendMessage" \
    -H "Content-Type: application/json" \
    -d "{\"chat_id\":\"${chat}\",\"text\":\"${text}\"}" \
    >/dev/null || echo "⚠️ Falló notificación Telegram." >&2
}

echo "🏛️ Supercommit_Max sobre rama: ${branch}"

if [[ "${SUPERCOMMIT_SKIP_BUILD:-0}" != "1" ]]; then
  echo "📦 npm install --no-fund --no-audit"
  npm install --no-fund --no-audit
  echo "🛠️ npm run build"
  npm run build
else
  echo "ℹ️ SUPERCOMMIT_SKIP_BUILD=1: build omitido."
fi

git add -A

if git diff --cached --quiet; then
  echo "ℹ️ Sin cambios para commit."
  commit_sha="$(git rev-parse --short HEAD)"
else
  git commit -m "$commit_msg"
  commit_sha="$(git rev-parse --short HEAD)"
fi

if [[ "${SUPERCOMMIT_SKIP_PUSH:-0}" != "1" ]]; then
  git push -u origin "$branch"
else
  echo "ℹ️ SUPERCOMMIT_SKIP_PUSH=1: push omitido."
fi

if [[ "${SUPERCOMMIT_DEPLOY:-0}" == "1" ]]; then
  if [[ -z "${VERCEL_TOKEN:-}" ]]; then
    echo "❌ SUPERCOMMIT_DEPLOY=1 pero VERCEL_TOKEN no está definido." >&2
    exit 3
  fi
  if ! command -v vercel >/dev/null 2>&1; then
    echo "❌ No se encontró CLI de vercel en PATH." >&2
    exit 3
  fi
  echo "🚀 vercel deploy --prod"
  vercel deploy --prod --yes --token="$VERCEL_TOKEN"
fi

notify_telegram "✅ @tryonyou_deploy_bot :: Supercommit_Max OK en rama ${branch} (commit ${commit_sha})."
echo "✅ Supercommit_Max completado."