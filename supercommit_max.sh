#!/usr/bin/env bash
set -euo pipefail

FAST=false
DEPLOY=false
MSG="chore(supercommit): sincronizar bunker oberkampf y galeria"

usage() {
  cat <<'EOF'
Uso: supercommit_max.sh [--fast] [--deploy] [--msg "mensaje"]

--fast    Omite typecheck/build previos.
--deploy  Ejecuta npm run deployall tras el push si hay cambios o no.
--msg     Asunto del commit; los sellos soberanos se anexan siempre.
EOF
}

notify_success() {
  local text="$1"
  local token chat
  token="${TRYONYOU_DEPLOY_BOT_TOKEN:-${TELEGRAM_BOT_TOKEN:-${TELEGRAM_TOKEN:-}}}"
  chat="${TRYONYOU_DEPLOY_CHAT_ID:-${TELEGRAM_CHAT_ID:-}}"
  token="$(printf '%s' "$token" | tr -d '[:space:]')"
  chat="$(printf '%s' "$chat" | tr -d '[:space:]')"
  if [[ -z "$token" || -z "$chat" || "${SKIP_TELEGRAM:-}" == "1" ]]; then
    echo "[supercommit_max] Telegram omitido: faltan token/chat en entorno seguro."
    return 0
  fi
  if ! command -v curl >/dev/null 2>&1; then
    echo "[supercommit_max] Telegram omitido: curl no disponible."
    return 0
  fi
  curl -fsS \
    --data-urlencode "chat_id=$chat" \
    --data-urlencode "text=$text" \
    "https://api.telegram.org/bot${token}/sendMessage" >/dev/null || \
    echo "[supercommit_max] Aviso: no se pudo enviar Telegram."
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
      [[ $# -ge 2 ]] || { echo "[supercommit_max] Falta valor para --msg" >&2; exit 2; }
      MSG="$2"
      shift 2
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      MSG="$1"
      shift
      ;;
  esac
done

BRANCH="$(git rev-parse --abbrev-ref HEAD)"
if [[ "$BRANCH" == "HEAD" ]]; then
  echo "[supercommit_max] Rama detached: no se puede empujar con seguridad." >&2
  exit 3
fi

if [[ "$FAST" != "true" ]]; then
  echo "[supercommit_max] Typecheck y build."
  npm run typecheck
  npm run build
fi

git add -A -- \
  ':!.env' \
  ':!.env.local' \
  ':!.env.*.local' \
  ':!.vercel' \
  ':!node_modules' \
  ':!dist' \
  ':!logs'

if [[ -n "$(git diff --cached --name-only)" ]]; then
  git commit -m "$(cat <<EOF
${MSG}

@CertezaAbsoluta @lo+erestu PCT/EP2025/067317 — Bajo Protocolo de Soberanía V10 - Founder: Rubén
EOF
)"
  git push -u origin "$BRANCH"
  notify_success "TryOnYou Supercommit_Max OK: ${BRANCH}"
else
  echo "[supercommit_max] Nada que commitear."
  git push -u origin "$BRANCH"
  notify_success "TryOnYou Supercommit_Max OK sin cambios: ${BRANCH}"
fi

if [[ "$DEPLOY" == "true" ]]; then
  echo "[supercommit_max] deployall solicitado."
  npm run deployall
fi