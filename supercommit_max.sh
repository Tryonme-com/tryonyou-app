#!/usr/bin/env bash
set -euo pipefail

FAST=false
DEPLOY=false
USER_MESSAGE="chore: sincronizar bunker Oberkampf con galeria web"

notify_success() {
  local token="${TRYONYOU_DEPLOY_BOT_TOKEN:-${TELEGRAM_BOT_TOKEN:-${TELEGRAM_TOKEN:-}}}"
  local chat_id="${TRYONYOU_DEPLOY_CHAT_ID:-${TELEGRAM_CHAT_ID:-}}"
  local message="$1"

  token="$(printf '%s' "$token" | tr -d '[:space:]')"
  if [[ -z "$token" || -z "$chat_id" ]]; then
    echo "[supercommit_max] Notificacion omitida: faltan token/chat_id en entorno."
    return 0
  fi
  if ! command -v curl >/dev/null 2>&1; then
    echo "[supercommit_max] Notificacion omitida: curl no disponible."
    return 0
  fi

  curl --fail --silent --show-error \
    --request POST "https://api.telegram.org/bot${token}/sendMessage" \
    --data-urlencode "chat_id=${chat_id}" \
    --data-urlencode "text=${message}" >/dev/null || {
      echo "[supercommit_max] Aviso: Telegram rechazo la notificacion." >&2
      return 0
    }
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --fast) FAST=true ;;
    --deploy) DEPLOY=true ;;
    --msg)
      if [[ $# -lt 2 || -z "${2:-}" ]]; then
        echo "[supercommit_max] --msg requiere un mensaje." >&2
        exit 2
      fi
      USER_MESSAGE="$2"
      shift
      ;;
    *)
      echo "[supercommit_max] Flag no reconocida: $1" >&2
      exit 2
      ;;
  esac
  shift
done

if [[ "$FAST" != "true" ]]; then
  echo "[supercommit_max] Typecheck y build."
  npm run typecheck
  npm run build
fi

if [[ -z "$(git status --porcelain)" ]]; then
  echo "[supercommit_max] Nada que commitear."
  exit 0
fi

git status --porcelain=v1 -z |
  while IFS= read -r -d '' entry; do
    path="${entry:3}"
    case "$path" in
      .env|.env.local|.env.*.local|*.pem|*.key|*.p12|*.pfx|*.crt|logs/*|node_modules/*|dist/*)
        echo "[supercommit_max] Excluido por seguridad: $path"
        ;;
      *)
        git add -- "$path"
        ;;
    esac
  done

if git diff --cached --quiet; then
  echo "[supercommit_max] Nada seguro que commitear tras aplicar exclusiones."
  exit 0
fi

git commit -m "$(cat <<EOF
$USER_MESSAGE

@CertezaAbsoluta @lo+erestu PCT/EP2025/067317 - Bajo Protocolo de Soberanía V10 - Founder: Rubén
EOF
)"

branch="$(git branch --show-current)"
if [[ -z "$branch" ]]; then
  echo "[supercommit_max] No hay rama git activa." >&2
  exit 1
fi

git push -u origin "$branch"

if [[ "$DEPLOY" == "true" ]]; then
  echo "[supercommit_max] deployall (puede desplegar si hay VERCEL_TOKEN)."
  npm run deployall
fi

notify_success "Supercommit_Max OK: bunker Oberkampf 75011 sincronizado con galeria web en ${branch}."