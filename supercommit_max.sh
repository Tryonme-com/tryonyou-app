#!/usr/bin/env bash
set -euo pipefail

FAST=false
DEPLOY=false
COMMIT_SUBJECT="chore: sincronizar bunker Oberkampf con galeria web"
SEAL="@CertezaAbsoluta @lo+erestu PCT/EP2025/067317 - Bajo Protocolo de Soberanía V10 - Founder: Rubén"

usage() {
  cat <<'EOF'
Uso: bash supercommit_max.sh [--fast] [--deploy] [--msg "mensaje"]

--fast      Omite typecheck/build local.
--deploy    Ejecuta npm run deployall tras commit/push si existe VERCEL_TOKEN.
--msg       Asunto del commit; se sellan automaticamente patente y protocolo.
EOF
}

notify_success() {
  local message="$1"
  local token="${TRYONYOU_DEPLOY_BOT_TOKEN:-${TELEGRAM_BOT_TOKEN:-${TELEGRAM_TOKEN:-}}}"
  local chat_id="${TRYONYOU_DEPLOY_CHAT_ID:-${TRYONYOU_DEPLOY_BOT_CHAT_ID:-${TELEGRAM_CHAT_ID:-}}}"

  if [[ -z "${token}" || -z "${chat_id}" ]]; then
    echo "[supercommit_max] Telegram omitido: falta token/chat_id en entorno."
    return 0
  fi

  python3 - "$token" "$chat_id" "$message" <<'PY'
import json
import sys
import urllib.parse
import urllib.request

token, chat_id, text = sys.argv[1:4]
token = "".join(token.split())
url = f"https://api.telegram.org/bot{token}/sendMessage"
payload = urllib.parse.urlencode({"chat_id": chat_id, "text": text}).encode()
try:
    with urllib.request.urlopen(url, data=payload, timeout=20) as response:
        body = json.loads(response.read().decode("utf-8"))
    if not body.get("ok"):
        print("[supercommit_max] Telegram respondio sin ok.", file=sys.stderr)
except Exception as exc:
    print(f"[supercommit_max] Telegram no confirmado: {exc}", file=sys.stderr)
PY
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
      if [[ $# -lt 2 ]]; then
        echo "[supercommit_max] --msg requiere valor." >&2
        exit 2
      fi
      COMMIT_SUBJECT="$2"
      shift 2
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

if [[ "$FAST" != "true" ]]; then
  echo "[supercommit_max] Typecheck y build."
  npm run typecheck
  npm run build
fi

if [[ -z "$(git status --porcelain)" ]]; then
  echo "[supercommit_max] Nada que commitear."
  notify_success "TryOnYou Supercommit_Max sin cambios pendientes en $(git branch --show-current)."
  exit 0
fi

echo "[supercommit_max] Staging seguro."
git ls-files --modified --others --exclude-standard -z \
  ':!:*.pem' ':!:*.key' ':!:*.p12' ':!:*.pfx' ':!:*.crt' \
  ':!:.env' ':!:.env.*' ':!:logs/*' ':!:node_modules/*' ':!:dist/*' \
  | xargs -0 -r git add --

if git diff --cached --quiet; then
  echo "[supercommit_max] Sin cambios seguros para commitear."
  exit 0
fi

git commit -m "$(cat <<EOF
${COMMIT_SUBJECT}

${SEAL}
EOF
)"

branch="$(git branch --show-current)"
if [[ -z "$branch" ]]; then
  echo "[supercommit_max] No hay rama activa para push." >&2
  exit 1
fi

git push -u origin "$branch"
notify_success "TryOnYou Supercommit_Max OK: bunker Oberkampf 75011 sincronizado con galeria web en ${branch}."

if [[ "$DEPLOY" == "true" ]]; then
  if [[ -z "${VERCEL_TOKEN:-}" ]]; then
    echo "[supercommit_max] Deploy omitido: falta VERCEL_TOKEN."
    exit 1
  fi
  echo "[supercommit_max] deployall."
  npm run deployall
  notify_success "TryOnYou deployall OK tras Supercommit_Max en ${branch}."
fi