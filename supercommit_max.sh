#!/usr/bin/env bash
set -euo pipefail

FAST=false
DEPLOY=false
MESSAGE="fix(merge): resolver conflictos y restaurar typecheck"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --fast) FAST=true ;;
    --deploy) DEPLOY=true ;;
    --msg)
      shift
      if [[ $# -eq 0 ]]; then
        echo "[supercommit_max] --msg requiere un valor." >&2
        exit 2
      fi
      MESSAGE="$1"
      ;;
    *)
      echo "[supercommit_max] Flag no reconocida: $1" >&2
      exit 2
      ;;
  esac
  shift
done

notify_success() {
  local text="$1"
  local token="${TRYONYOU_DEPLOY_BOT_TOKEN:-${TELEGRAM_BOT_TOKEN:-${TELEGRAM_TOKEN:-}}}"
  local chat_id="${TRYONYOU_DEPLOY_CHAT_ID:-${TELEGRAM_CHAT_ID:-}}"

  if [[ -z "$token" || -z "$chat_id" ]]; then
    echo "[supercommit_max] Telegram omitido: faltan token/chat_id en entorno."
    return 0
  fi

  if ! command -v curl >/dev/null 2>&1; then
    echo "[supercommit_max] Telegram omitido: curl no disponible."
    return 0
  fi

  curl -fsS \
    -X POST "https://api.telegram.org/bot${token}/sendMessage" \
    -d "chat_id=${chat_id}" \
    --data-urlencode "text=${text}" >/dev/null || \
    echo "[supercommit_max] Aviso: Telegram no confirmó el envío." >&2
}

is_sensitive_path() {
  case "$1" in
    .env|.env.*|*/.env|*/.env.*|*.pem|*.key|*.p12|*.pfx|*.crt|node_modules/*|dist/*|logs/*)
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
      echo "[supercommit_max] Excluido del commit: $path"
      continue
    fi
    git add -- "$path"
  done < <(git ls-files --modified --others --exclude-standard -z)
}

if [[ "$FAST" != "true" ]]; then
  echo "[supercommit_max] Typecheck y build."
  npm run typecheck
  npm run build
fi

if [[ -z "$(git status --porcelain)" ]]; then
  echo "[supercommit_max] Nada que commitear."
  notify_success "TryOnYou Supercommit_Max OK: sin cambios pendientes en $(git branch --show-current)."
  exit 0
fi

stage_safe_changes

if git diff --cached --quiet; then
  echo "[supercommit_max] No hay cambios seguros para commitear."
  exit 0
fi

git commit -m "$(cat <<EOF
${MESSAGE}

@CertezaAbsoluta @lo+erestu PCT/EP2025/067317 — Bajo Protocolo de Soberanía V10 - Founder: Rubén
EOF
)"

branch="$(git branch --show-current)"
if [[ -z "$branch" ]]; then
  echo "[supercommit_max] No hay rama actual para push." >&2
  exit 1
fi

git push -u origin "$branch"

if [[ "$DEPLOY" == "true" ]]; then
  echo "[supercommit_max] deployall (puede desplegar si hay VERCEL_TOKEN)."
  npm run deployall
fi

notify_success "TryOnYou Supercommit_Max OK: ${branch} sincronizada con typecheck/build."