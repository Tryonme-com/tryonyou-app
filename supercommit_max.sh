#!/usr/bin/env bash
set -euo pipefail

FAST=false
DEPLOY=false
VALIDATE_ONLY=false
RELEASE_MESSAGE="chore(release): sincronizar bunker Oberkampf con galeria web"
SOVEREIGN_STAMP="@CertezaAbsoluta @lo+erestu PCT/EP2025/067317"
PROTOCOL_STAMP="Bajo Protocolo de Soberanía V10 - Founder: Rubén"

usage() {
  cat <<'EOF'
Uso: bash supercommit_max.sh [--fast] [--deploy] [--validate-only] [--msg "mensaje"]

Opciones:
  --fast           Omite typecheck/build locales.
  --deploy         Ejecuta npm run deployall tras push correcto.
  --validate-only  Valida argumentos y sintaxis sin commitear ni pushear.
  --msg MENSAJE    Mensaje base del commit; los sellos soberanos se anexan siempre.
EOF
}

notify_success() {
  local text="$1"
  if [[ "${SKIP_TELEGRAM:-}" == "1" ]]; then
    echo "[supercommit_max] Telegram omitido por SKIP_TELEGRAM=1."
    return 0
  fi

  local token="${TRYONYOU_DEPLOY_BOT_TOKEN:-${TELEGRAM_BOT_TOKEN:-${TELEGRAM_TOKEN:-}}}"
  local chat_id="${TRYONYOU_DEPLOY_CHAT_ID:-${TELEGRAM_CHAT_ID:-}}"
  if [[ -z "$token" || -z "$chat_id" ]]; then
    echo "[supercommit_max] Telegram omitido: falta token o chat_id en entorno."
    return 0
  fi
  if ! command -v curl >/dev/null 2>&1; then
    echo "[supercommit_max] Telegram omitido: curl no disponible."
    return 0
  fi

  curl --fail --silent --show-error \
    --data-urlencode "chat_id=$chat_id" \
    --data-urlencode "text=$text" \
    "https://api.telegram.org/bot${token}/sendMessage" >/dev/null || {
      echo "[supercommit_max] Aviso: Telegram no confirmó la notificación." >&2
      return 0
    }
}

build_commit_message() {
  local base="$1"
  printf "%s\n\n%s\n%s\n" "$base" "$SOVEREIGN_STAMP" "$PROTOCOL_STAMP"
}

is_safe_stage_path() {
  case "$1" in
    .env|.env.*|node_modules/*|dist/*|logs/*|*.pem|*.key|*.p12|*.pfx|*.crt)
      [[ "$1" == ".env.example" ]]
      ;;
    *)
      return 0
      ;;
  esac
}

stage_safe_changes() {
  local tracked=()
  local untracked=()
  local path

  while IFS= read -r -d '' path; do
    if is_safe_stage_path "$path"; then
      tracked+=("$path")
    fi
  done < <(git ls-files --modified --deleted -z -- .)

  while IFS= read -r -d '' path; do
    if is_safe_stage_path "$path"; then
      untracked+=("$path")
    fi
  done < <(git ls-files --others --exclude-standard -z -- .)

  if [[ ${#tracked[@]} -gt 0 ]]; then
    git add -- "${tracked[@]}"
  fi

  if [[ ${#untracked[@]} -gt 0 ]]; then
    git add -- "${untracked[@]}"
  fi
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
    --validate-only)
      VALIDATE_ONLY=true
      shift
      ;;
    --msg)
      if [[ $# -lt 2 || -z "${2:-}" ]]; then
        echo "[supercommit_max] --msg requiere un valor." >&2
        exit 2
      fi
      RELEASE_MESSAGE="$2"
      shift 2
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
done

if [[ "$VALIDATE_ONLY" == "true" ]]; then
  echo "[supercommit_max] Validacion OK."
  exit 0
fi

BRANCH="$(git branch --show-current)"
if [[ -z "$BRANCH" ]]; then
  echo "[supercommit_max] No hay rama git activa; abortando push." >&2
  exit 1
fi

if [[ "$FAST" != "true" ]]; then
  echo "[supercommit_max] Typecheck y build."
  npm run typecheck
  npm run build
fi

if [[ -z "$(git status --porcelain)" ]]; then
  echo "[supercommit_max] Nada que commitear."
  notify_success "Supercommit_Max sin cambios en ${BRANCH}. Bunker Oberkampf 75011 sincronizado con galeria web."
  exit 0
fi

stage_safe_changes

if git diff --cached --quiet; then
  echo "[supercommit_max] Solo habia cambios excluidos por seguridad; nada que commitear."
  exit 0
fi

git commit -m "$(build_commit_message "$RELEASE_MESSAGE")"
git push -u origin "$BRANCH"

if [[ "$DEPLOY" == "true" ]]; then
  echo "[supercommit_max] deployall (requiere entorno de despliegue configurado)."
  npm run deployall
fi

notify_success "Supercommit_Max OK en ${BRANCH}: bunker Oberkampf 75011 sincronizado con galeria web."