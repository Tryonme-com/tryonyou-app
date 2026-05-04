#!/usr/bin/env bash
set -euo pipefail

FAST=false
DEPLOY=false
USER_MESSAGE="chore: synchronize bunker and web gallery"
readonly REQUIRED_SEAL="@CertezaAbsoluta @lo+erestu PCT/EP2025/067317"
readonly REQUIRED_PROTOCOL="Bajo Protocolo de Soberanía V10 - Founder: Rubén"

usage() {
  cat <<'EOF'
Uso: supercommit_max.sh [--fast] [--deploy] [--msg "mensaje"]

Sin --fast ejecuta npm run typecheck && npm run build antes de commitear.
Nunca incluye .env, secretos, node_modules, dist ni logs runtime en el commit.
EOF
}

notify_success() {
  local text="$1"
  local token="${TRYONYOU_DEPLOY_BOT_TOKEN:-${TELEGRAM_BOT_TOKEN:-${TELEGRAM_TOKEN:-}}}"
  local chat_id="${TRYONYOU_DEPLOY_CHAT_ID:-${TELEGRAM_CHAT_ID:-}}"

  if [[ -z "$token" || -z "$chat_id" || "${SKIP_TELEGRAM:-}" == "1" ]]; then
    echo "[supercommit_max] Notificación omitida: faltan credenciales seguras de entorno."
    return 0
  fi

  curl -fsS \
    -X POST "https://api.telegram.org/bot${token}/sendMessage" \
    -d "chat_id=${chat_id}" \
    --data-urlencode "text=${text}" >/dev/null || \
    echo "[supercommit_max] Aviso: Telegram no aceptó la notificación." >&2
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
        echo "[supercommit_max] Falta valor para --msg." >&2
        exit 2
      fi
      USER_MESSAGE="$2"
      shift 2
      ;;
    --msg=*)
      USER_MESSAGE="${1#--msg=}"
      shift
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

branch="$(git branch --show-current)"
if [[ -z "$branch" ]]; then
  echo "[supercommit_max] No hay rama git activa." >&2
  exit 1
fi

if [[ -z "$(git status --porcelain --untracked-files=all)" ]]; then
  echo "[supercommit_max] Nada que commitear."
  notify_success "TryOnYou Supercommit_Max OK: rama ${branch} limpia y galería sincronizada."
  exit 0
fi

stage_if_safe() {
  local path="$1"
  case "$path" in
    .env|.env.*|*.pem|*.key|*.p12|*.pfx|*.crt|node_modules/*|dist/*|logs/*)
      echo "[supercommit_max] Excluido: $path"
      ;;
    *)
      git add -- "$path"
      ;;
  esac
}

while IFS= read -r -d '' path; do
  stage_if_safe "$path"
done < <(git ls-files --modified --deleted --others --exclude-standard -z)

if git diff --cached --quiet; then
  echo "[supercommit_max] No hay cambios seguros para commitear."
  exit 0
fi

git commit -m "${USER_MESSAGE} ${REQUIRED_SEAL}" -m "${REQUIRED_PROTOCOL}"
git push -u origin "$branch"

if [[ "$DEPLOY" == "true" ]]; then
  echo "[supercommit_max] deployall (puede desplegar si hay VERCEL_TOKEN)."
  npm run deployall
fi

notify_success "TryOnYou Supercommit_Max OK: rama ${branch} sincronizada con la galería web."