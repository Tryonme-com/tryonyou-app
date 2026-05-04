#!/usr/bin/env bash
# Supercommit_Max — sincronizacion segura bunker Oberkampf (75011) <-> galeria web.
#
# Patente: PCT/EP2025/067317
# Bajo Protocolo de Soberanía V10 - Founder: Rubén
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"

FAST=0
DEPLOY=0
USER_MSG=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --fast)
      FAST=1
      shift
      ;;
    --deploy)
      DEPLOY=1
      shift
      ;;
    --msg|-m)
      if [[ $# -lt 2 ]]; then
        echo "Uso: $0 [--fast] [--deploy] [--msg \"mensaje\"]" >&2
        exit 64
      fi
      USER_MSG="$2"
      shift 2
      ;;
    --help|-h)
      echo "Uso: $0 [--fast] [--deploy] [--msg \"mensaje\"]"
      exit 0
      ;;
    *)
      echo "Argumento desconocido: $1" >&2
      exit 64
      ;;
  esac
done

notify_telegram() {
  local status="$1"
  local text="$2"

  if [[ "${SKIP_TELEGRAM:-}" == "1" ]]; then
    return 0
  fi

  local token="${TRYONYOU_DEPLOY_BOT_TOKEN:-${TELEGRAM_BOT_TOKEN:-${TELEGRAM_TOKEN:-}}}"
  local chat_id="${TRYONYOU_DEPLOY_CHAT_ID:-${TELEGRAM_CHAT_ID:-}}"
  if [[ -z "$token" || -z "$chat_id" ]]; then
    echo "Telegram omitido: falta TRYONYOU_DEPLOY_BOT_TOKEN/TELEGRAM_BOT_TOKEN o chat_id." >&2
    return 0
  fi

  TELEGRAM_TOKEN_VALUE="$token" TELEGRAM_CHAT_ID_VALUE="$chat_id" TELEGRAM_TEXT_VALUE="[$status] $text" \
    python3 - <<'PY' || true
import os
import urllib.parse
import urllib.request

token = os.environ["TELEGRAM_TOKEN_VALUE"]
chat_id = os.environ["TELEGRAM_CHAT_ID_VALUE"]
text = os.environ["TELEGRAM_TEXT_VALUE"]
data = urllib.parse.urlencode({"chat_id": chat_id, "text": text}).encode("utf-8")
url = f"https://api.telegram.org/bot{token}/sendMessage"
req = urllib.request.Request(url, data=data, method="POST")
with urllib.request.urlopen(req, timeout=10) as resp:
    resp.read()
PY
}

on_exit() {
  local code=$?
  if [[ $code -ne 0 ]]; then
    notify_telegram "ERROR" "Supercommit_Max fallo en ${GITHUB_REF_NAME:-$(git branch --show-current 2>/dev/null || echo unknown)}."
  fi
}
trap on_exit EXIT

seal_message() {
  local msg="$1"
  [[ "$msg" == *"@CertezaAbsoluta"* ]] || msg="$msg @CertezaAbsoluta"
  [[ "$msg" == *"@lo+erestu"* ]] || msg="$msg @lo+erestu"
  [[ "$msg" == *"PCT/EP2025/067317"* ]] || msg="$msg PCT/EP2025/067317"
  [[ "$msg" == *"Bajo Protocolo de Soberanía V10 - Founder: Rubén"* ]] || msg="$msg Bajo Protocolo de Soberanía V10 - Founder: Rubén"
  printf '%s\n' "$msg"
}

is_sensitive_path() {
  local path="$1"
  case "$path" in
    .env|.env.*|*/.env|*/.env.*|logs/*|*.pem|*.key|*.p12|*.pfx|*.crt)
      return 0
      ;;
    *)
      return 1
      ;;
  esac
}

stage_safe_changes() {
  local path

  while IFS= read -r -d '' path; do
    if is_sensitive_path "$path"; then
      echo "No se stagea ruta sensible: $path" >&2
      continue
    fi
    git add -- "$path"
  done < <(git diff --name-only -z)

  while IFS= read -r -d '' path; do
    if is_sensitive_path "$path"; then
      echo "No se stagea ruta sensible: $path" >&2
      continue
    fi
    git add -- "$path"
  done < <(git ls-files --others --exclude-standard -z)
}

run_gallery_checks() {
  if [[ $FAST -eq 1 ]]; then
    echo "Modo --fast: se omiten checks de galeria."
    return 0
  fi

  if ! command -v npm >/dev/null 2>&1; then
    echo "npm no disponible en PATH; se omiten checks frontend locales." >&2
    return 0
  fi

  if [[ -f package-lock.json && ! -d node_modules ]]; then
    npm install
  fi

  npm run typecheck

  if [[ $DEPLOY -eq 1 ]]; then
    npm run build
  fi
}

main() {
  local branch
  branch="$(git branch --show-current)"
  if [[ -z "$branch" ]]; then
    echo "No se puede ejecutar Supercommit_Max en HEAD detached." >&2
    exit 65
  fi

  run_gallery_checks
  stage_safe_changes

  if git diff --cached --quiet; then
    notify_telegram "OK" "Supercommit_Max sin cambios pendientes en $branch."
    echo "Sin cambios seguros que commitear."
    return 0
  fi

  local msg
  msg="$(seal_message "${USER_MSG:-chore: Supercommit_Max sincroniza bunker Oberkampf 75011 con galeria web}")"

  git commit -m "$msg"
  git push -u origin "$branch"
  notify_telegram "OK" "Supercommit_Max ejecutado y sincronizado en $branch."
}

main "$@"