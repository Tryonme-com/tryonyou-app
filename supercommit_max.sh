#!/usr/bin/env bash
# Supercommit_Max TryOnYou:
# - Sincroniza búnker local con galería web (build + git push en rama activa)
# - Reporta éxito al bot de despliegue por Telegram
# Patente: PCT/EP2025/067317

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT_DIR"

# Carga variables operativas locales sin exponer secretos.
if [[ -f "$ROOT_DIR/.env" ]]; then
  set -a
  # shellcheck disable=SC1091
  source "$ROOT_DIR/.env"
  set +a
fi

REQUIRED_TAG_1="@CertezaAbsoluta"
REQUIRED_TAG_2="@lo+erestu"
REQUIRED_PATENT="PCT/EP2025/067317"
REQUIRED_FOUNDER="Bajo Protocolo de Soberanía V10 - Founder: Rubén"

BUILD_ENABLED=1
PUSH_ENABLED=1
TELEGRAM_REQUIRED=1
COMMIT_MESSAGE="chore: Supercommit Max bunker-web sync"

usage() {
  cat <<'EOF'
Uso:
  ./supercommit_max.sh [-m "mensaje"] [--skip-build] [--skip-push] [--allow-missing-telegram]

Variables de entorno:
  TRYONYOU_DEPLOY_BOT_TOKEN   Token bot Telegram (alternativa: TELEGRAM_BOT_TOKEN o TELEGRAM_TOKEN)
  TRYONYOU_DEPLOY_CHAT_ID     Chat destino Telegram (alternativa: TELEGRAM_CHAT_ID)
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    -m|--message)
      [[ $# -lt 2 ]] && { echo "Falta valor para $1" >&2; exit 2; }
      COMMIT_MESSAGE="$2"
      shift 2
      ;;
    --skip-build)
      BUILD_ENABLED=0
      shift
      ;;
    --skip-push)
      PUSH_ENABLED=0
      shift
      ;;
    --allow-missing-telegram)
      TELEGRAM_REQUIRED=0
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Argumento no reconocido: $1" >&2
      usage
      exit 2
      ;;
  esac
done

append_if_missing() {
  local base="$1"
  local piece="$2"
  if [[ "$base" == *"$piece"* ]]; then
    printf '%s' "$base"
  else
    printf '%s %s' "$base" "$piece"
  fi
}

FULL_COMMIT_MESSAGE="$COMMIT_MESSAGE"
FULL_COMMIT_MESSAGE="$(append_if_missing "$FULL_COMMIT_MESSAGE" "$REQUIRED_TAG_1")"
FULL_COMMIT_MESSAGE="$(append_if_missing "$FULL_COMMIT_MESSAGE" "$REQUIRED_TAG_2")"
FULL_COMMIT_MESSAGE="$(append_if_missing "$FULL_COMMIT_MESSAGE" "$REQUIRED_PATENT")"
FULL_COMMIT_MESSAGE="$(append_if_missing "$FULL_COMMIT_MESSAGE" "$REQUIRED_FOUNDER")"

CURRENT_BRANCH="$(git branch --show-current)"
if [[ -z "$CURRENT_BRANCH" ]]; then
  echo "No se pudo detectar la rama activa." >&2
  exit 2
fi

if [[ $BUILD_ENABLED -eq 1 ]]; then
  if [[ -f package.json ]]; then
    echo ">> npm install --no-fund --no-audit"
    npm install --no-fund --no-audit
    echo ">> npm run build"
    npm run build
  else
    echo "package.json no encontrado: build omitido."
  fi
fi

git add -A
if git diff --cached --quiet; then
  echo "No hay cambios para commitear."
else
  git commit -m "$FULL_COMMIT_MESSAGE"
fi

if [[ $PUSH_ENABLED -eq 1 ]]; then
  git push -u origin "$CURRENT_BRANCH"
fi

telegram_notify_success() {
  local token
  local chat_id
  local text

  token="${TRYONYOU_DEPLOY_BOT_TOKEN:-${TELEGRAM_BOT_TOKEN:-${TELEGRAM_TOKEN:-}}}"
  chat_id="${TRYONYOU_DEPLOY_CHAT_ID:-${TELEGRAM_CHAT_ID:-7868120279}}"

  if [[ -z "$token" || -z "$chat_id" ]]; then
    if [[ $TELEGRAM_REQUIRED -eq 1 ]]; then
      echo "Faltan credenciales Telegram (token/chat_id) para notificar éxito." >&2
      return 1
    fi
    echo "Telegram no configurado; notificación omitida."
    return 0
  fi

  text="✅ Supercommit_Max OK
Bot: @tryonyou_deploy_bot
Branch: $CURRENT_BRANCH
Repo: tryonyou-app
Sync: Búnker Oberkampf 75011 ↔ Galería Web"

  if ! curl -fsS "https://api.telegram.org/bot${token}/sendMessage" \
    --data-urlencode "chat_id=${chat_id}" \
    --data-urlencode "text=${text}" \
    >/dev/null; then
    if [[ $TELEGRAM_REQUIRED -eq 1 ]]; then
      echo "Falló la notificación Telegram requerida." >&2
      return 1
    fi
    echo "Telegram no disponible; notificación omitida."
    return 0
  fi
  echo "Notificación Telegram entregada."
}

telegram_notify_success
echo "Supercommit_Max finalizado sin errores."