#!/usr/bin/env bash
set -euo pipefail

FAST=false
DEPLOY=false
MSG="sync: Supercommit_Max bunker galeria"
REMOTE="${SUPERCOMMIT_REMOTE:-origin}"
BRANCH="${SUPERCOMMIT_BRANCH:-$(git branch --show-current)}"
PATENT_SEAL="@CertezaAbsoluta @lo+erestu PCT/EP2025/067317"
SOVEREIGN_SEAL="Bajo Protocolo de Soberanía V10 - Founder: Rubén"

notify_success() {
  local message="$1"
  local token="${TRYONYOU_DEPLOY_BOT_TOKEN:-${TELEGRAM_BOT_TOKEN:-${TELEGRAM_TOKEN:-}}}"
  local chat="${TRYONYOU_DEPLOY_CHAT_ID:-${TELEGRAM_CHAT_ID:-}}"
  if [[ -z "$token" || -z "$chat" ]]; then
    echo "[supercommit_max] Telegram omitido: falta token/chat_id en entorno."
    return 0
  fi
  python3 - "$token" "$chat" "$message" <<'PY'
import json
import sys
import urllib.parse
import urllib.request

token, chat, text = sys.argv[1:4]
data = urllib.parse.urlencode({"chat_id": chat, "text": text}).encode("utf-8")
req = urllib.request.Request(
    f"https://api.telegram.org/bot{token}/sendMessage",
    data=data,
    headers={"Content-Type": "application/x-www-form-urlencoded"},
    method="POST",
)
try:
    with urllib.request.urlopen(req, timeout=12) as resp:
        payload = json.loads(resp.read().decode("utf-8"))
    if not payload.get("ok"):
        print("[supercommit_max] Telegram no confirmado por API.", file=sys.stderr)
except Exception as exc:  # noqa: BLE001 - script shell: nunca romper commit/push por aviso.
    print(f"[supercommit_max] Telegram falló: {exc}", file=sys.stderr)
PY
}

while [[ $# -gt 0 ]]; do
  arg="$1"
  case "$arg" in
    --fast) FAST=true ;;
    --deploy) DEPLOY=true ;;
    --msg)
      shift
      if [[ $# -eq 0 ]]; then
        echo "[supercommit_max] --msg requiere texto." >&2
        exit 2
      fi
      MSG="$1"
      ;;
    *)
      echo "[supercommit_max] Flag no reconocida: $arg" >&2
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
  notify_success "TryOnYou Supercommit_Max: sin cambios que commitear en ${BRANCH}."
  exit 0
fi

git add -A -- .
git reset -q -- \
  .env \
  .env.* \
  '*.pem' \
  '*.key' \
  '*.p12' \
  '*.pfx' \
  '*.crt' \
  logs/ 2>/dev/null || true

if [[ -z "$(git diff --cached --name-only)" ]]; then
  echo "[supercommit_max] Nada seguro que commitear tras exclusiones."
  exit 0
fi

if [[ "$MSG" != *"@CertezaAbsoluta"* ]]; then
  MSG="${MSG} ${PATENT_SEAL}"
fi
if [[ "$MSG" != *"Bajo Protocolo de Soberanía V10 - Founder: Rubén"* ]]; then
  MSG="${MSG} ${SOVEREIGN_SEAL}"
fi

git commit -m "$MSG"
git push -u "$REMOTE" "$BRANCH"
notify_success "TryOnYou Supercommit_Max OK: ${BRANCH} sincronizada con galería web."

if [[ "$DEPLOY" == "true" ]]; then
  echo "[supercommit_max] deployall (puede desplegar si hay VERCEL_TOKEN)."
  npm run deployall
  notify_success "TryOnYou deployall completado desde Supercommit_Max en ${BRANCH}."
fi