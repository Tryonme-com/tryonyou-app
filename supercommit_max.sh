#!/usr/bin/env bash
set -euo pipefail

FAST=false
DEPLOY=false
COMMIT_MESSAGE="chore: sincronizar bunker Oberkampf con galeria web"
PATENT="PCT/EP2025/067317"
PROTOCOL="Bajo Protocolo de Soberanía V10 - Founder: Rubén"

while [[ $# -gt 0 ]]; do
  arg="$1"
  case "$arg" in
    --fast) FAST=true ;;
    --deploy) DEPLOY=true ;;
    --msg)
      shift
      if [[ $# -eq 0 ]]; then
        echo "[supercommit_max] --msg requiere un valor." >&2
        exit 2
      fi
      COMMIT_MESSAGE="$1"
      ;;
    --msg=*)
      COMMIT_MESSAGE="${arg#--msg=}"
      ;;
    *)
      echo "[supercommit_max] Flag no reconocida: $arg" >&2
      exit 2
      ;;
  esac
  shift
done

seal_commit_message() {
  local message="$1"
  [[ "$message" == *"@CertezaAbsoluta"* ]] || message="${message}"$'\n\n''@CertezaAbsoluta @lo+erestu '"$PATENT"
  [[ "$message" == *"@lo+erestu"* ]] || message="${message}"$'\n''@lo+erestu'
  [[ "$message" == *"$PATENT"* ]] || message="${message}"$'\n'"$PATENT"
  [[ "$message" == *"$PROTOCOL"* ]] || message="${message}"$'\n'"$PROTOCOL"
  printf '%s\n' "$message"
}

notify_tryonyou_deploy_bot() {
  local text="$1"
  local token="${TRYONYOU_DEPLOY_BOT_TOKEN:-${TELEGRAM_BOT_TOKEN:-${TELEGRAM_TOKEN:-}}}"
  local chat_id="${TRYONYOU_DEPLOY_CHAT_ID:-${TELEGRAM_CHAT_ID:-}}"
  if [[ -z "$token" || -z "$chat_id" ]]; then
    echo "[supercommit_max] Telegram omitido: falta TRYONYOU_DEPLOY_BOT_TOKEN/TELEGRAM_* o chat_id."
    return 0
  fi
  TELEGRAM_BOT_TOKEN="$token" TELEGRAM_CHAT_ID="$chat_id" TELEGRAM_TEXT="$text" python3 - <<'PY'
import json
import os
import sys
import urllib.error
import urllib.request

token = os.environ["TELEGRAM_BOT_TOKEN"]
payload = json.dumps({
    "chat_id": os.environ["TELEGRAM_CHAT_ID"],
    "text": os.environ["TELEGRAM_TEXT"],
}).encode("utf-8")
request = urllib.request.Request(
    f"https://api.telegram.org/bot{token}/sendMessage",
    data=payload,
    headers={"Content-Type": "application/json"},
    method="POST",
)
try:
    with urllib.request.urlopen(request, timeout=20) as response:
        if response.status != 200:
            print(f"[supercommit_max] Telegram HTTP {response.status}", file=sys.stderr)
except urllib.error.URLError as exc:
    print(f"[supercommit_max] Telegram no enviado: {exc}", file=sys.stderr)
PY
}

is_safe_to_stage() {
  local path="$1"
  case "$path" in
    .env.example) return 0 ;;
    .env|.env.*|*/.env|*/.env.*|*.pem|*.key|*.p12|*.pfx|*.crt|logs/*|*/logs/*|node_modules/*|*/node_modules/*|dist/*|*/dist/*)
      return 1
      ;;
    *)
      return 0
      ;;
  esac
}

if [[ "$FAST" != "true" ]]; then
  echo "[supercommit_max] Typecheck y build."
  npm run typecheck
  npm run build
fi

mapfile -d '' changed_paths < <(git ls-files -z --modified --deleted --others --exclude-standard)
safe_paths=()
for path in "${changed_paths[@]}"; do
  if is_safe_to_stage "$path"; then
    safe_paths+=("$path")
  else
    echo "[supercommit_max] Excluido del stage seguro: $path"
  fi
done

if [[ ${#safe_paths[@]} -eq 0 ]]; then
  echo "[supercommit_max] Nada que commitear."
  notify_tryonyou_deploy_bot "TRYONYOU Supercommit_Max OK: sin cambios pendientes en $(git rev-parse --abbrev-ref HEAD). $PATENT"
  exit 0
fi

git add -- "${safe_paths[@]}"

git commit -m "$(seal_commit_message "$COMMIT_MESSAGE")"

branch="$(git rev-parse --abbrev-ref HEAD)"
git push -u origin "$branch"

if [[ "$DEPLOY" == "true" ]]; then
  echo "[supercommit_max] deployall (puede desplegar si hay VERCEL_TOKEN)."
  npm run deployall
fi

notify_tryonyou_deploy_bot "TRYONYOU Supercommit_Max OK: búnker Oberkampf 75011 sincronizado con galería web en rama ${branch}. $PATENT"