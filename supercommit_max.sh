#!/usr/bin/env bash
# Supercommit_Max TryOnYou:
# - sincroniza bunker Oberkampf (75011) con la galeria web
# - ejecuta validacion de seguridad Fatality (martes 08:00, 450.000 EUR)
# - commit + push al branch actual (sin forzar)
# - notifica exito por Telegram si hay credenciales
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT_DIR"

PATENT_TAG="PCT/EP2025/067317"
FOUNDER_TAG="Bajo Protocolo de Soberania V10 - Founder: Ruben"
REQUIRED_TAGS=("@CertezaAbsoluta" "@lo+erestu" "$PATENT_TAG" "$FOUNDER_TAG")
BOT_USERNAME="${TRYONYOU_DEPLOY_BOT_USERNAME:-@tryonyou_deploy_bot}"

TOKEN="${TRYONYOU_DEPLOY_BOT_TOKEN:-${TELEGRAM_BOT_TOKEN:-${TELEGRAM_TOKEN:-}}}"
CHAT_ID="${TRYONYOU_DEPLOY_BOT_CHAT_ID:-${TELEGRAM_CHAT_ID:-}}"

DEFAULT_MSG="chore: Supercommit_Max sincroniza Oberkampf 75011 con galeria web"
CLI_MSG="${1:-$DEFAULT_MSG}"
COMMIT_TEXT="$CLI_MSG"
BRANCH="$(git rev-parse --abbrev-ref HEAD)"
DRY_RUN="${SUPERCOMMIT_DRY_RUN:-0}"

append_required_tags() {
  local tag
  for tag in "${REQUIRED_TAGS[@]}"; do
    if [[ "$COMMIT_TEXT" != *"$tag"* ]]; then
      COMMIT_TEXT="$COMMIT_TEXT $tag"
    fi
  done
}

notify_success() {
  local text="$1"
  if [[ -z "${TOKEN}" || -z "${CHAT_ID}" ]]; then
    echo "INFO: Telegram no configurado; se omite notificacion ($BOT_USERNAME)."
    return 0
  fi
  curl -sS -X POST "https://api.telegram.org/bot${TOKEN}/sendMessage" \
    -d "chat_id=${CHAT_ID}" \
    --data-urlencode "text=${text}" \
    -d "parse_mode=HTML" >/dev/null
  echo "OK: Notificacion enviada por ${BOT_USERNAME}."
}

git_push_retry() {
  local attempt=1
  local sleep_secs=4
  local max_attempts=5
  while (( attempt <= max_attempts )); do
    if git push -u origin "$BRANCH"; then
      return 0
    fi
    if (( attempt == max_attempts )); then
      return 1
    fi
    echo "WARN: git push fallo. Reintento ${attempt}/${max_attempts} en ${sleep_secs}s..."
    sleep "$sleep_secs"
    sleep_secs=$((sleep_secs * 2))
    attempt=$((attempt + 1))
  done
}

run_git_stage_commit_push() {
  git add -A
  if git diff --cached --quiet; then
    echo "INFO: No hay cambios para commit."
    return 0
  fi
  if [[ "$DRY_RUN" == "1" ]]; then
    echo "INFO: SUPERCOMMIT_DRY_RUN=1, commit/push omitidos."
    echo "INFO: Mensaje de commit previsto: $COMMIT_TEXT"
    return 0
  fi
  git commit -m "$COMMIT_TEXT"
  git_push_retry
}

run_build() {
  if [[ "${SUPERCOMMIT_SKIP_BUILD:-0}" == "1" ]]; then
    echo "INFO: SUPERCOMMIT_SKIP_BUILD=1, se omite npm run build."
    return 0
  fi
  if [[ ! -f "package.json" ]]; then
    echo "INFO: Sin package.json, se omite build web."
    return 0
  fi
  echo "[Supercommit_Max] Build de galeria web..."
  npm run build
}

echo "Iniciando Supercommit_Max (Oberkampf 75011 -> galeria web)"

if [[ -f "$ROOT_DIR/security_tuesday_fatality.py" ]]; then
  echo "Ejecutando check de seguridad Fatality..."
  python3 "$ROOT_DIR/security_tuesday_fatality.py"
fi

run_build
append_required_tags

run_git_stage_commit_push

notify_success "OK: Supercommit_Max completado en branch ${BRANCH}. Oberkampf 75011 sincronizado con la galeria web."
echo "OK: Supercommit_Max finalizado."