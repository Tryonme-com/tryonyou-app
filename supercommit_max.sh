#!/usr/bin/env bash
set -euo pipefail

FAST=false
DEPLOY=false
USER_MSG="chore: sincronizar bunker Oberkampf con galeria web"
REQUIRED_STAMP="@CertezaAbsoluta @lo+erestu PCT/EP2025/067317"
PROTOCOL_STAMP="Bajo Protocolo de Soberanía V10 - Founder: Rubén"

usage() {
  cat <<'EOF'
Uso: bash supercommit_max.sh [--fast] [--deploy] [--msg "mensaje"]

  --fast       Omite typecheck/build local.
  --deploy     Ejecuta npm run deployall tras commit/push.
  --msg TEXT   Mensaje base del commit; los sellos soberanos se inyectan solos.
EOF
}

notify_success() {
  local text="$1"
  local token chat url
  token="${TRYONYOU_DEPLOY_BOT_TOKEN:-${TELEGRAM_BOT_TOKEN:-${TELEGRAM_TOKEN:-}}}"
  chat="${TRYONYOU_DEPLOY_CHAT_ID:-${TELEGRAM_CHAT_ID:-}}"

  if [[ -z "$token" || -z "$chat" ]]; then
    echo "[supercommit_max] Telegram omitido: falta token/chat en entorno."
    return 0
  fi
  if ! command -v curl >/dev/null 2>&1; then
    echo "[supercommit_max] Telegram omitido: curl no disponible."
    return 0
  fi

  url="https://api.telegram.org/bot${token}/sendMessage"
  curl --fail --silent --show-error \
    --request POST \
    --header "Content-Type: application/json" \
    --data "{\"chat_id\":\"${chat}\",\"text\":\"${text}\",\"disable_web_page_preview\":true}" \
    "$url" >/dev/null || echo "[supercommit_max] Aviso: Telegram no aceptó la notificación."
}

append_required_stamps() {
  local msg="$1"
  [[ "$msg" == *"$REQUIRED_STAMP"* ]] || msg="${msg}"$'\n\n'"${REQUIRED_STAMP}"
  [[ "$msg" == *"$PROTOCOL_STAMP"* ]] || msg="${msg}"$'\n'"${PROTOCOL_STAMP}"
  printf '%s\n' "$msg"
}

is_safe_path() {
  local path="$1"
  case "$path" in
    .env|.env.*|*/.env|*/.env.*) return 1 ;;
    node_modules/*|*/node_modules/*) return 1 ;;
    dist/*|*/dist/*) return 1 ;;
    logs/*|*/logs/*) return 1 ;;
    *.pem|*.key|*.p12|*.pfx|*.crt) return 1 ;;
  esac
  return 0
}

stage_safe_changes() {
  local -a paths=()
  local path
  while IFS= read -r -d '' path; do
    if is_safe_path "$path"; then
      paths+=("$path")
    else
      echo "[supercommit_max] Excluido del stage seguro: $path"
    fi
  done < <(git ls-files -z --modified --deleted --others --exclude-standard)

  if (( ${#paths[@]} == 0 )); then
    echo "[supercommit_max] No hay cambios seguros que stagear."
    return 1
  fi

  git add -- "${paths[@]}"
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
      if [[ $# -lt 2 || -z "${2:-}" ]]; then
        echo "[supercommit_max] --msg requiere texto." >&2
        exit 2
      fi
      USER_MSG="$2"
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
else
  stage_safe_changes
  if [[ -z "$(git diff --cached --name-only)" ]]; then
    echo "[supercommit_max] Solo había cambios excluidos por seguridad."
  else
    COMMIT_TEXT="$(append_required_stamps "$USER_MSG")"
    git commit -m "$COMMIT_TEXT"
    BRANCH="$(git branch --show-current)"
    if [[ -z "$BRANCH" ]]; then
      echo "[supercommit_max] No se pudo resolver la rama actual." >&2
      exit 1
    fi
    git push -u origin "$BRANCH"
    notify_success "TryOnYou: Supercommit_Max OK en ${BRANCH}"
  fi
fi

if [[ "$DEPLOY" == "true" ]]; then
  echo "[supercommit_max] deployall (puede desplegar si hay VERCEL_TOKEN)."
  npm run deployall
  notify_success "TryOnYou: deployall OK tras Supercommit_Max"
fi