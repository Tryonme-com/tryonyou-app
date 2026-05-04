#!/usr/bin/env bash
set -euo pipefail

FAST=false
DEPLOY=false
COMMIT_SUBJECT="chore(supercommit): sincronizar bunker Oberkampf con galeria web"
PROTOCOL_STAMP="@CertezaAbsoluta @lo+erestu PCT/EP2025/067317 - Bajo Protocolo de Soberania V10 - Founder: Ruben"

notify_success() {
  local text="$1"
  local token="${TRYONYOU_DEPLOY_BOT_TOKEN:-${TELEGRAM_BOT_TOKEN:-${TELEGRAM_TOKEN:-}}}"
  local chat_id="${TRYONYOU_DEPLOY_CHAT_ID:-${TELEGRAM_CHAT_ID:-}}"

  if [[ -z "$token" || -z "$chat_id" || "${SKIP_TELEGRAM:-0}" == "1" ]]; then
    echo "[supercommit_max] Telegram omitido: falta token/chat_id o SKIP_TELEGRAM=1."
    return 0
  fi

  curl --fail --silent --show-error \
    --request POST "https://api.telegram.org/bot${token}/sendMessage" \
    --data-urlencode "chat_id=${chat_id}" \
    --data-urlencode "text=${text}" \
    --data-urlencode "parse_mode=${TELEGRAM_FORMAT:-}" >/dev/null
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
        echo "[supercommit_max] --msg requiere un asunto de commit." >&2
        exit 2
      fi
      COMMIT_SUBJECT="$2"
      shift 2
      ;;
    *)
      echo "[supercommit_max] Flag no reconocida: $1" >&2
      exit 2
      ;;
  esac
done

if [[ "$FAST" != "true" ]]; then
  echo "[supercommit_max] Typecheck y build."
  npm run typecheck
  npm run build
fi

if [[ -z "$(git status --porcelain)" ]]; then
  echo "[supercommit_max] Nada que commitear."
else
  git add -A -- ':!*.env' ':!*.env.*' ':!*.pem' ':!*.key' ':!*.p12' ':!*.pfx' ':!*.crt' ':!logs/*'

  if [[ -z "$(git diff --cached --name-only)" ]]; then
    echo "[supercommit_max] Sin cambios versionables tras excluir secretos/runtime."
  else
    git commit -m "$(cat <<EOF
${COMMIT_SUBJECT}

${PROTOCOL_STAMP}
EOF
)"
    current_branch="$(git rev-parse --abbrev-ref HEAD)"
    git push -u origin "$current_branch"
    notify_success "OK Supercommit_Max: bunker Oberkampf 75011 sincronizado con galeria web en ${current_branch}."
  fi
fi

if [[ "$DEPLOY" == "true" ]]; then
  echo "[supercommit_max] deployall (puede desplegar si hay VERCEL_TOKEN)."
  npm run deployall
  notify_success "OK deployall: galeria web ejecutada desde Supercommit_Max."
fi