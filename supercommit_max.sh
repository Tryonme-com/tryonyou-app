#!/usr/bin/env bash
set -euo pipefail

FAST=false
DEPLOY=false
SUPERCOMMIT_MESSAGE="sync: ejecutar Supercommit_Max bunker galeria"
VALIDATE_ONLY="${SUPERCOMMIT_VALIDATE_ONLY:-}"
REQUIRED_SEAL="@CertezaAbsoluta @lo+erestu PCT/EP2025/067317"
REQUIRED_PROTOCOL="Bajo Protocolo de Soberanía V10 - Founder: Rubén"

usage() {
  cat <<'EOF'
Uso: bash supercommit_max.sh [--fast] [--deploy] [--msg "mensaje"]

Sin --fast ejecuta npm run typecheck && npm run build antes del commit.
El staging excluye .env, logs y material sensible; no hardcodea tokens.
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --fast) FAST=true ;;
    --deploy) DEPLOY=true ;;
    --msg)
      shift
      if [[ $# -eq 0 || -z "${1:-}" ]]; then
        echo "[supercommit_max] --msg requiere texto." >&2
        exit 2
      fi
      SUPERCOMMIT_MESSAGE="$1"
      ;;
    --help|-h)
      usage
      exit 0
      ;;
    *)
      echo "[supercommit_max] Flag no reconocida: $1" >&2
      usage >&2
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

notify_success() {
  local text="$1"
  local token="${TRYONYOU_DEPLOY_BOT_TOKEN:-${TELEGRAM_BOT_TOKEN:-${TELEGRAM_TOKEN:-}}}"
  local chat_id="${TRYONYOU_DEPLOY_CHAT_ID:-${TELEGRAM_CHAT_ID:-}}"

  if [[ -z "$token" || -z "$chat_id" || -n "${SKIP_TELEGRAM:-}" ]]; then
    echo "[supercommit_max] Notificación Telegram omitida (faltan variables o SKIP_TELEGRAM activo)."
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
    method="POST",
)
try:
    with urllib.request.urlopen(request, timeout=15) as response:
        json.loads(response.read().decode("utf-8"))
except Exception as exc:  # noqa: BLE001 - notificación no debe romper el commit/push.
    print(f"[supercommit_max] Telegram no confirmado: {exc}", file=sys.stderr)
PY
}

safe_stage() {
  git reset --quiet
  while IFS= read -r path; do
    case "$path" in
      .env|.env.local|.env.*.local|*/.env|*/.env.local|*/.env.*.local|logs/*|*/logs/*|node_modules/*|dist/*|*.pem|*.key|*.p12|*.pfx|*.crt)
        echo "[supercommit_max] Excluido del staging: $path"
        ;;
      *)
        git add -- "$path"
        ;;
    esac
  done < <(git ls-files --modified --others --deleted --exclude-standard)
}

if [[ -z "$(git status --porcelain)" ]]; then
  echo "[supercommit_max] Nada que commitear."
  exit 0
fi

safe_stage

if [[ -z "$(git diff --cached --name-only)" ]]; then
  echo "[supercommit_max] No hay cambios seguros para commitear."
  exit 0
fi

if [[ "$SUPERCOMMIT_MESSAGE" != *"@CertezaAbsoluta"* || "$SUPERCOMMIT_MESSAGE" != *"@lo+erestu"* || "$SUPERCOMMIT_MESSAGE" != *"PCT/EP2025/067317"* ]]; then
  SUPERCOMMIT_MESSAGE="${SUPERCOMMIT_MESSAGE}

${REQUIRED_SEAL}"
fi

if [[ "$SUPERCOMMIT_MESSAGE" != *"Bajo Protocolo de Soberanía V10 - Founder: Rubén"* ]]; then
  SUPERCOMMIT_MESSAGE="${SUPERCOMMIT_MESSAGE}
${REQUIRED_PROTOCOL}"
fi

if [[ -n "$VALIDATE_ONLY" ]]; then
  echo "[supercommit_max] VALIDATE_ONLY activo; staging verificado sin commit."
  exit 0
fi

git commit -m "$SUPERCOMMIT_MESSAGE"

if [[ "$DEPLOY" == "true" ]]; then
  echo "[supercommit_max] deployall (puede desplegar si hay VERCEL_TOKEN)."
  npm run deployall
fi

branch="$(git branch --show-current)"
if [[ -z "$branch" ]]; then
  echo "[supercommit_max] No se pudo resolver la rama actual." >&2
  exit 3
fi

git push -u origin "$branch"
notify_success "Supercommit_Max OK: bunker Oberkampf 75011 sincronizado con galeria web en rama ${branch}."