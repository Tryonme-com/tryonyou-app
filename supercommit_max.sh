#!/usr/bin/env bash
set -euo pipefail

FAST=false
DEPLOY=false
COMMIT_MESSAGE="chore(supercommit): sincronizar bunker Oberkampf 75011 con galeria web"

REQUIRED_STAMP="@CertezaAbsoluta @lo+erestu PCT/EP2025/067317"
SOVEREIGN_STAMP="Bajo Protocolo de Soberanía V10 - Founder: Rubén"

usage() {
  cat <<'EOF'
Uso: bash supercommit_max.sh [--fast] [--deploy] [--msg "mensaje"]

Sincroniza el bunker de Oberkampf (75011) con la galeria web en la rama actual:
  - ejecuta typecheck/build salvo --fast
  - stage seguro sin .env, certificados, llaves ni logs
  - commit sellado con protocolo TryOnYou
  - push normal a origin/<rama-actual>
  - notificacion opcional por Telegram via variables de entorno

Variables Telegram:
  TRYONYOU_DEPLOY_BOT_TOKEN o TELEGRAM_BOT_TOKEN o TELEGRAM_TOKEN
  TRYONYOU_DEPLOY_CHAT_ID o TELEGRAM_CHAT_ID
EOF
}

notify_success() {
  local message="$1"
  local token="${TRYONYOU_DEPLOY_BOT_TOKEN:-${TELEGRAM_BOT_TOKEN:-${TELEGRAM_TOKEN:-}}}"
  local chat_id="${TRYONYOU_DEPLOY_CHAT_ID:-${TELEGRAM_CHAT_ID:-}}"

  if [[ -z "$token" || -z "$chat_id" ]]; then
    echo "[supercommit_max] Telegram no configurado: se omite notificacion."
    return 0
  fi

  if ! command -v curl >/dev/null 2>&1; then
    echo "[supercommit_max] curl no disponible: se omite notificacion."
    return 0
  fi

  curl --silent --show-error --fail \
    --request POST \
    --data-urlencode "chat_id=${chat_id}" \
    --data-urlencode "text=${message}" \
    "https://api.telegram.org/bot${token}/sendMessage" >/dev/null || {
      echo "[supercommit_max] Aviso: fallo la notificacion Telegram." >&2
      return 0
    }
}

safe_stage() {
  local new_files=()

  git add -u

  while IFS= read -r -d '' path; do
    case "$path" in
      .env|.env.*|*.pem|*.key|*.p12|*.pfx|*.crt|logs|logs/*) ;;
      *) new_files+=("$path") ;;
    esac
  done < <(git ls-files --others --exclude-standard -z)

  if [[ ${#new_files[@]} -gt 0 ]]; then
    git add -- "${new_files[@]}"
  fi
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --fast) FAST=true ;;
    --deploy) DEPLOY=true ;;
    --msg)
      shift
      if [[ $# -eq 0 || -z "${1:-}" ]]; then
        echo "[supercommit_max] --msg requiere un valor." >&2
        exit 2
      fi
      COMMIT_MESSAGE="$1"
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
  shift
done

BRANCH="$(git branch --show-current)"
if [[ -z "$BRANCH" ]]; then
  echo "[supercommit_max] No hay rama git activa; abortando push seguro." >&2
  exit 2
fi

if [[ "$FAST" != "true" ]]; then
  echo "[supercommit_max] Typecheck y build."
  npm run typecheck
  npm run build
fi

if [[ -z "$(git status --porcelain)" ]]; then
  echo "[supercommit_max] Nada que commitear."
  notify_success "TryOnYou Supercommit_Max OK: bunker Oberkampf 75011 y galeria web ya sincronizados en ${BRANCH}."
  exit 0
fi

safe_stage

if [[ -z "$(git diff --cached --name-only)" ]]; then
  echo "[supercommit_max] Solo habia cambios excluidos por seguridad; nada que commitear."
  notify_success "TryOnYou Supercommit_Max OK: sin cambios publicables en ${BRANCH}."
  exit 0
fi

git commit -m "${COMMIT_MESSAGE}

${REQUIRED_STAMP}
${SOVEREIGN_STAMP}" --no-verify

LAST_COMMIT="$(git rev-parse --short HEAD)"
git push -u origin "$BRANCH"

if [[ "$DEPLOY" == "true" ]]; then
  echo "[supercommit_max] deployall (puede desplegar si hay VERCEL_TOKEN)."
  npm run deployall
fi

notify_success "TryOnYou Supercommit_Max OK: bunker Oberkampf 75011 sincronizado con galeria web. Rama ${BRANCH}, commit ${LAST_COMMIT}."