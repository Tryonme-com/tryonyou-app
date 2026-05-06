#!/usr/bin/env bash
set -euo pipefail

FAST=false
DEPLOY=false
MESSAGE="chore(supercommit): sincronizar bunker oberkampf y galeria"

trim() {
  local value="${1:-}"
  value="${value#"${value%%[![:space:]]*}"}"
  value="${value%"${value##*[![:space:]]}"}"
  printf '%s' "$value"
}

notify_success() {
  local text="$1"
  if [[ "${SKIP_TELEGRAM:-}" == "1" ]]; then
    echo "[supercommit_max] Telegram omitido por SKIP_TELEGRAM=1."
    return 0
  fi

  local token chat_id
  token="$(trim "${TRYONYOU_DEPLOY_BOT_TOKEN:-${TELEGRAM_BOT_TOKEN:-${TELEGRAM_TOKEN:-}}}")"
  chat_id="$(trim "${TRYONYOU_DEPLOY_CHAT_ID:-${TELEGRAM_CHAT_ID:-}}")"
  if [[ -z "$token" || -z "$chat_id" ]]; then
    echo "[supercommit_max] Telegram omitido: falta token o chat id en entorno."
    return 0
  fi

  curl -fsS -X POST "https://api.telegram.org/bot${token}/sendMessage" \
    --data-urlencode "chat_id=${chat_id}" \
    --data-urlencode "text=${text}" \
    >/dev/null
}

while (($#)); do
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
      if [[ $# -lt 2 ]]; then
        echo "[supercommit_max] --msg requiere un mensaje." >&2
        exit 2
      fi
      MESSAGE="$2"
      shift 2
      ;;
    --*)
      echo "[supercommit_max] Flag no reconocida: $1" >&2
      exit 2
      ;;
    *)
      MESSAGE="$1"
      shift
      ;;
  esac
done

BRANCH="$(git branch --show-current)"
if [[ -z "$BRANCH" ]]; then
  echo "[supercommit_max] No hay rama git activa." >&2
  exit 2
fi

if [[ "$FAST" != "true" ]]; then
  echo "[supercommit_max] Typecheck y build."
  npm run typecheck
  npm run build
fi

git add -A -- .
git reset -q -- .env .env.* .vercel node_modules dist logs 2>/dev/null || true

if git diff --cached --name-only -z | xargs -0 -r rg -n "[0-9]{8,12}:[A-Za-z0-9_-]{20,}" >/dev/null; then
  echo "[supercommit_max] Posible token de Telegram detectado en staging. Abortando." >&2
  exit 1
fi

if git diff --cached --quiet; then
  echo "[supercommit_max] Nada que commitear."
  git push -u origin "$BRANCH"
  notify_success "OK TryOnYou Supercommit_Max sin cambios en ${BRANCH}"
  exit 0
fi

git commit -m "$(cat <<EOF
${MESSAGE}

@CertezaAbsoluta @lo+erestu PCT/EP2025/067317 - Bajo Protocolo de Soberanía V10 - Founder: Rubén
EOF
)"

git push -u origin "$BRANCH"

if [[ "$DEPLOY" == "true" ]]; then
  echo "[supercommit_max] deployall (despliega solo si deployall tiene credenciales seguras)."
  npm run deployall
fi

notify_success "OK TryOnYou Supercommit_Max: ${MESSAGE} (${BRANCH})"