#!/usr/bin/env bash
# supercommit_max.sh - checks opcionales, commit con sellos TryOnYou, push seguro y deploy opcional.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"

FAST_MODE=false
DEPLOY_MODE=false
COMMIT_MSG_RAW=""
DEFAULT_MSG="OMEGA_DEPLOY: sincronizacion del bunker Oberkampf (75011) con la galeria web."

REQUIRED_STAMPS=(
  "@CertezaAbsoluta"
  "@lo+erestu"
  "PCT/EP2025/067317"
  "Bajo Protocolo de Soberanía V10 - Founder: Rubén"
)

usage() {
  cat <<'EOF'
Uso:
  bash supercommit_max.sh [--fast] [--deploy] [--msg "mensaje"]
  bash supercommit_max.sh "mensaje libre"

Opciones:
  --fast       Omite tests/typecheck/build previos.
  --deploy     Ejecuta npm run deployall tras commit/push.
  --msg TEXT   Mensaje base. Los sellos TryOnYou se anaden si faltan.
EOF
}

append_missing_stamps() {
  local message="$1"
  local stamp=""
  for stamp in "${REQUIRED_STAMPS[@]}"; do
    if [[ "$message" != *"$stamp"* ]]; then
      message="${message} ${stamp}"
    fi
  done
  printf "%s" "$message"
}

log_step() {
  printf "\n==> %s\n" "$1"
}

notify_success() {
  local text="${1:-}"
  local token="${TRYONYOU_DEPLOY_BOT_TOKEN:-${TELEGRAM_BOT_TOKEN:-${TELEGRAM_TOKEN:-}}}"
  local chat_id="${TRYONYOU_DEPLOY_CHAT_ID:-${TELEGRAM_CHAT_ID:-}}"
  local branch short_sha

  token="$(printf '%s' "$token" | tr -d '[:space:]')"
  chat_id="$(printf '%s' "$chat_id" | tr -d '[:space:]')"

  if [[ -z "$token" || -z "$chat_id" ]]; then
    echo "[supercommit_max] Notificacion Telegram omitida: falta token/chat en entorno."
    return 0
  fi

  branch="$(git rev-parse --abbrev-ref HEAD 2>/dev/null || printf 'unknown')"
  short_sha="$(git rev-parse --short HEAD 2>/dev/null || printf 'unknown')"
  if [[ -z "$text" ]]; then
    text="TryOnYou Supercommit_Max OK | branch=${branch} | sha=${short_sha}"
  fi

  if ! TRYONYOU_NOTIFY_TEXT="$text" TRYONYOU_NOTIFY_TOKEN="$token" TRYONYOU_NOTIFY_CHAT_ID="$chat_id" python3 - <<'PY'
import json
import os
import urllib.error
import urllib.request

token = os.environ["TRYONYOU_NOTIFY_TOKEN"]
chat_id = os.environ["TRYONYOU_NOTIFY_CHAT_ID"]
text = os.environ["TRYONYOU_NOTIFY_TEXT"]
payload = json.dumps({"chat_id": chat_id, "text": text}).encode("utf-8")
request = urllib.request.Request(
    f"https://api.telegram.org/bot{token}/sendMessage",
    data=payload,
    headers={"Content-Type": "application/json"},
    method="POST",
)
try:
    with urllib.request.urlopen(request, timeout=10) as response:
        if response.status >= 300:
            raise SystemExit(f"telegram_status_{response.status}")
except (urllib.error.URLError, TimeoutError) as exc:
    raise SystemExit(f"telegram_error:{exc}")
PY
  then
    echo "[supercommit_max] Notificacion Telegram fallida; commit/push conservados."
  fi
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --fast)
      FAST_MODE=true
      shift
      ;;
    --deploy)
      DEPLOY_MODE=true
      shift
      ;;
    --msg)
      if [[ $# -lt 2 || -z "${2:-}" ]]; then
        echo "[supercommit_max] --msg requiere texto." >&2
        usage >&2
        exit 2
      fi
      COMMIT_MSG_RAW="$2"
      shift 2
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      if [[ -z "$COMMIT_MSG_RAW" ]]; then
        COMMIT_MSG_RAW="$1"
      else
        COMMIT_MSG_RAW="$COMMIT_MSG_RAW $1"
      fi
      shift
      ;;
  esac
done

if [[ -z "$COMMIT_MSG_RAW" ]]; then
  COMMIT_MSG_RAW="$DEFAULT_MSG"
fi
FINAL_MSG="$(append_missing_stamps "$COMMIT_MSG_RAW")"

branch_name="$(git rev-parse --abbrev-ref HEAD)"
if [[ -z "$branch_name" || "$branch_name" == "HEAD" ]]; then
  echo "[supercommit_max] No hay rama git actual." >&2
  exit 1
fi

if [[ "$FAST_MODE" == false ]]; then
  log_step "Python tests"
  python3 -m unittest discover -s tests -p 'test_*.py' -v

  log_step "TypeScript type-check"
  npx tsc --noEmit

  log_step "Vite production build"
  npm run build
fi

if [[ -z "$(git status --porcelain)" ]]; then
  echo "[supercommit_max] Nada que commitear."
  notify_success "TryOnYou Supercommit_Max OK: sin cambios pendientes en ${branch_name}."
else
  log_step "Git add seguro"
  git add -A .
  git reset -q -- \
    .env \
    .env.local \
    .env.*.local \
    .vercel \
    node_modules \
    dist \
    logs \
    2>/dev/null || true

  if git diff --cached --quiet; then
    echo "[supercommit_max] No hay cambios seguros para commitear tras aplicar exclusiones."
    notify_success "TryOnYou Supercommit_Max OK: cambios no versionables omitidos en ${branch_name}."
  else
    log_step "Git commit"
    git commit -m "$FINAL_MSG"

    log_step "Git push"
    git push -u origin "$branch_name"

    notify_success "TryOnYou Supercommit_Max OK: ${COMMIT_MSG_RAW} en ${branch_name}."
  fi
fi

if [[ "$DEPLOY_MODE" == true ]]; then
  log_step "Deployall"
  npm run deployall
fi
