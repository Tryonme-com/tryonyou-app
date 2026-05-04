#!/usr/bin/env bash
set -euo pipefail

FAST=false
DEPLOY=false
VALIDATE_ONLY="${SUPERCOMMIT_VALIDATE_ONLY:-0}"
REQUESTED_MESSAGE=""

REQUIRED_SEAL="@CertezaAbsoluta @lo+erestu PCT/EP2025/067317"
SOVEREIGN_PROTOCOL="Bajo Protocolo de Soberanía V10 - Founder: Rubén"

notify_deploy_bot() {
  local text="$1"
  local token="${TRYONYOU_DEPLOY_BOT_TOKEN:-${TELEGRAM_BOT_TOKEN:-${TELEGRAM_TOKEN:-}}}"
  local chat_id="${TRYONYOU_DEPLOY_CHAT_ID:-${TELEGRAM_CHAT_ID:-}}"

  if [[ -z "$token" || -z "$chat_id" || "${SKIP_TELEGRAM:-}" == "1" ]]; then
    echo "[supercommit_max] Notificación Telegram omitida (token/chat_id no configurados)."
    return 0
  fi

  python3 - "$token" "$chat_id" "$text" <<'PY'
import json
import sys
import urllib.parse
import urllib.request

token, chat_id, text = sys.argv[1:4]
payload = urllib.parse.urlencode({"chat_id": chat_id, "text": text}).encode()
request = urllib.request.Request(
    f"https://api.telegram.org/bot{token}/sendMessage",
    data=payload,
    headers={"Content-Type": "application/x-www-form-urlencoded"},
)
try:
    with urllib.request.urlopen(request, timeout=10) as response:
        data = json.loads(response.read().decode("utf-8"))
except Exception as exc:  # pragma: no cover - network/environment dependent
    print(f"[supercommit_max] Telegram no enviado: {exc}", file=sys.stderr)
    sys.exit(0)
if not data.get("ok"):
    print(f"[supercommit_max] Telegram rechazado: {data}", file=sys.stderr)
PY
}

build_commit_message() {
  local subject="${1:-chore: sincronizar bunker Oberkampf con galeria web}"
  if [[ "$subject" != *"$REQUIRED_SEAL"* ]]; then
    subject+=$'\n\n'"$REQUIRED_SEAL"
  fi
  if [[ "$subject" != *"$SOVEREIGN_PROTOCOL"* ]]; then
    subject+=" - $SOVEREIGN_PROTOCOL"
  fi
  printf '%s\n' "$subject"
}

stage_safe_changes() {
  local path
  while IFS= read -r path; do
    case "$path" in
      .env|.env.*|*/.env|*/.env.*|*.pem|*.key|*.p12|*.pfx|*.crt|logs/*|*/logs/*|node_modules/*|dist/*)
        echo "[supercommit_max] Excluido del stage seguro: $path"
        ;;
      *)
        git add -- "$path"
        ;;
    esac
  done < <(git status --porcelain=v1 | sed -E 's/^.{3}//')
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --fast) FAST=true ;;
    --deploy) DEPLOY=true ;;
    --msg)
      shift
      if [[ $# -eq 0 ]]; then
        echo "[supercommit_max] --msg requiere un texto." >&2
        exit 2
      fi
      REQUESTED_MESSAGE="$1"
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
  notify_deploy_bot "Supercommit_Max OK: sin cambios pendientes en $(git rev-parse --abbrev-ref HEAD)."
  exit 0
fi

stage_safe_changes

if [[ "$VALIDATE_ONLY" == "1" ]]; then
  echo "[supercommit_max] Validación de staging completada; commit omitido por SUPERCOMMIT_VALIDATE_ONLY=1."
  exit 0
fi

if [[ -z "$(git diff --cached --name-only)" ]]; then
  echo "[supercommit_max] No hay cambios seguros para commitear tras aplicar exclusiones."
  exit 0
fi

git commit -m "$(build_commit_message "$REQUESTED_MESSAGE")"

BRANCH="$(git rev-parse --abbrev-ref HEAD)"
git push -u origin "$BRANCH"

if [[ "$DEPLOY" == "true" ]]; then
  echo "[supercommit_max] deployall (puede desplegar si hay VERCEL_TOKEN)."
  npm run deployall
fi

notify_deploy_bot "Supercommit_Max OK: bunker Oberkampf 75011 sincronizado con galeria web en ${BRANCH}."