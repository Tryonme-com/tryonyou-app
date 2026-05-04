#!/usr/bin/env bash
set -euo pipefail

FAST=false
DEPLOY=false
USER_MESSAGE="sync: Supercommit_Max bunker Oberkampf galerie web"
VALIDATE_ONLY="${SUPERCOMMIT_VALIDATE_ONLY:-}"

REQUIRED_STAMP="@CertezaAbsoluta @lo+erestu PCT/EP2025/067317"
PROTOCOL_STAMP="Bajo Protocolo de Soberanía V10 - Founder: Rubén"

notify_deploy_bot() {
  local text="$1"
  local token="${TRYONYOU_DEPLOY_BOT_TOKEN:-${TELEGRAM_BOT_TOKEN:-${TELEGRAM_TOKEN:-}}}"
  local chat_id="${TRYONYOU_DEPLOY_CHAT_ID:-${TELEGRAM_CHAT_ID:-}}"

  if [[ -z "$token" || -z "$chat_id" ]]; then
    echo "[supercommit_max] Telegram omitido: faltan TRYONYOU_DEPLOY_BOT_TOKEN/CHAT_ID o TELEGRAM_*."
    return 0
  fi

  if ! command -v curl >/dev/null 2>&1; then
    echo "[supercommit_max] Telegram omitido: curl no disponible."
    return 0
  fi

  curl -fsS -X POST "https://api.telegram.org/bot${token}/sendMessage" \
    -d "chat_id=${chat_id}" \
    --data-urlencode "text=${text}" >/dev/null || {
      echo "[supercommit_max] Aviso: no se pudo notificar Telegram." >&2
      return 0
    }
}

build_commit_message() {
  printf "%s\n\n%s — %s\n" "$USER_MESSAGE" "$REQUIRED_STAMP" "$PROTOCOL_STAMP"
}

safe_stage_changes() {
  local path
  local -a files=()
  while IFS= read -r -d '' path; do
    case "$path" in
      .env|.env.*|node_modules/*|dist/*|logs/*|*.pem|*.key|*.p12|*.pfx|*.crt)
        continue
        ;;
    esac
    files+=("$path")
  done < <(git ls-files -m -d -o --exclude-standard -z)

  if [[ ${#files[@]} -gt 0 ]]; then
    git add -- "${files[@]}"
  fi
}

while [[ $# -gt 0 ]]; do
  arg="$1"
  case "$arg" in
    --fast) FAST=true ;;
    --deploy) DEPLOY=true ;;
    --msg)
      shift
      if [[ $# -eq 0 || -z "${1:-}" ]]; then
        echo "[supercommit_max] --msg requiere texto." >&2
        exit 2
      fi
      USER_MESSAGE="$1"
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

if [[ "$VALIDATE_ONLY" == "1" ]]; then
  echo "[supercommit_max] Validación completada (SUPERCOMMIT_VALIDATE_ONLY=1)."
  exit 0
fi

if [[ -z "$(git status --porcelain)" ]]; then
  echo "[supercommit_max] Nada que commitear."
  notify_deploy_bot "TryOnYou Supercommit_Max OK: rama limpia, sin cambios que publicar."
  exit 0
fi

safe_stage_changes

if git diff --cached --quiet; then
  echo "[supercommit_max] Solo había cambios ignorados/sensibles; no se crea commit."
  exit 0
fi

git commit -m "$(build_commit_message)"

branch="$(git branch --show-current)"
if [[ -z "$branch" ]]; then
  echo "[supercommit_max] No se pudo resolver la rama actual." >&2
  exit 1
fi

git push -u origin "$branch"

if [[ "$DEPLOY" == "true" ]]; then
  echo "[supercommit_max] deployall (puede desplegar si hay VERCEL_TOKEN)."
  npm run deployall
fi

notify_deploy_bot "TryOnYou Supercommit_Max OK: búnker Oberkampf 75011 sincronizado con galería web en rama ${branch}."