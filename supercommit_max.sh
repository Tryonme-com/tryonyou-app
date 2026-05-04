#!/usr/bin/env bash
set -euo pipefail

FAST=false
DEPLOY=false
COMMIT_MSG="chore: sincronizar bunker Oberkampf con galeria web"

notify_success() {
  local message="$1"
  local token="${TRYONYOU_DEPLOY_BOT_TOKEN:-${TELEGRAM_BOT_TOKEN:-${TELEGRAM_TOKEN:-}}}"
  local chat_id="${TRYONYOU_DEPLOY_CHAT_ID:-${TELEGRAM_CHAT_ID:-}}"

  if [[ -z "$token" || -z "$chat_id" || "${SKIP_TELEGRAM:-}" == "1" ]]; then
    echo "[supercommit_max] Notificación Telegram omitida: faltan credenciales o SKIP_TELEGRAM=1."
    return 0
  fi

  curl -fsS -X POST "https://api.telegram.org/bot${token}/sendMessage" \
    --data-urlencode "chat_id=${chat_id}" \
    --data-urlencode "text=${message}" \
    --data-urlencode "parse_mode=${TELEGRAM_FORMAT:-}" >/dev/null || {
      echo "[supercommit_max] Aviso: Telegram no confirmó la notificación." >&2
      return 0
    }
}

seal_commit_message() {
  local msg="$1"
  local seal="@CertezaAbsoluta @lo+erestu PCT/EP2025/067317"
  local protocol="Bajo Protocolo de Soberanía V10 - Founder: Rubén"

  [[ "$msg" == *"@CertezaAbsoluta"* ]] || msg="${msg}"$'\n\n'"${seal}"
  [[ "$msg" == *"Bajo Protocolo de Soberanía V10 - Founder: Rubén"* ]] || msg="${msg}"$'\n'"${protocol}"
  printf '%s' "$msg"
}

stage_safe_changes() {
  git add -A
  git reset -q -- .env ".env.*" "*.pem" "*.key" "*.p12" "*.pfx" "*.crt" "logs" 2>/dev/null || true
}

staged_names() {
  if git rev-parse --verify HEAD >/dev/null 2>&1; then
    git diff --cached --name-only
  else
    git diff --cached --name-only --root
  fi
}

current_branch() {
  local branch
  branch="$(git symbolic-ref --quiet --short HEAD 2>/dev/null || true)"
  if [[ -z "$branch" ]]; then
    branch="$(git rev-parse --abbrev-ref HEAD)"
  fi
  printf '%s' "$branch"
}

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
      COMMIT_MSG="$1"
      ;;
    --msg=*)
      COMMIT_MSG="${1#--msg=}"
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
  notify_success "TryOnYou Supercommit_Max OK: búnker Oberkampf 75011 sincronizado; galería web sin cambios pendientes."
  exit 0
fi

stage_safe_changes

if [[ -z "$(staged_names)" ]]; then
  echo "[supercommit_max] Solo había cambios sensibles/no versionables; nada que commitear."
  notify_success "TryOnYou Supercommit_Max OK: cambios sensibles excluidos; no hay commit publicable."
  exit 0
fi

BRANCH="$(current_branch)"
if [[ "$BRANCH" == "HEAD" ]]; then
  echo "[supercommit_max] No se puede hacer push desde detached HEAD." >&2
  exit 1
fi

git commit -m "$(seal_commit_message "$COMMIT_MSG")"

git push -u origin "$BRANCH"

if [[ "$DEPLOY" == "true" ]]; then
  echo "[supercommit_max] deployall (puede desplegar si hay VERCEL_TOKEN)."
  npm run deployall
fi

notify_success "TryOnYou Supercommit_Max OK: búnker Oberkampf 75011 sincronizado con la galería web en ${BRANCH}."