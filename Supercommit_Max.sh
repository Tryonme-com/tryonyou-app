#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"

if [[ -f "$ROOT/.env" ]]; then
  set -a
  # shellcheck disable=SC1091
  source "$ROOT/.env"
  set +a
fi

BOT_TOKEN="${TRYONYOU_DEPLOY_BOT_TOKEN:-${TELEGRAM_BOT_TOKEN:-${TELEGRAM_TOKEN:-}}}"
CHAT_ID="${TELEGRAM_CHAT_ID:-}"
SECURITY_LEDGER="${SECURITY_LEDGER:-$ROOT/logs/capital_inflows.json}"

notify_success() {
  local message="$1"
  if python3 "$ROOT/scripts/tryonyou_deploy_bot_notify.py" \
    --bot-token "$BOT_TOKEN" \
    --chat-id "$CHAT_ID" \
    --message "$message"; then
    return 0
  fi
  echo "⚠️ No se pudo reportar éxito al bot @tryonyou_deploy_bot (se continúa sin romper pipeline)."
  return 0
}

require_bot() {
  [[ -n "$BOT_TOKEN" ]] || {
    echo "❌ Falta token de @tryonyou_deploy_bot en TRYONYOU_DEPLOY_BOT_TOKEN/TELEGRAM_BOT_TOKEN/TELEGRAM_TOKEN."
    exit 2
  }
  [[ -n "$CHAT_ID" ]] || {
    echo "❌ Falta TELEGRAM_CHAT_ID para reportar éxitos."
    exit 2
  }
}

step() {
  printf "\n▸ %s\n" "$1"
}

require_bot

step "Supercommit_Max: sincronizando búnker Oberkampf (75011) con galería web"
bash "$ROOT/supercommit_max.sh" --msg "Supercommit_Max Oberkampf-75011 sincronizado con galería web"
notify_success "✅ Supercommit_Max completado: búnker Oberkampf 75011 sincronizado con galería web."

step "Monitor de liquidación instantánea"
python3 "$ROOT/auditoria_impacto_matinal.py" --liquidacion
notify_success "✅ Monitor de liquidación instantánea ejecutado sin errores de Bash."

step "Guardia de seguridad martes 08:00 (450.000€ + Dossier Fatality)"
if python3 "$ROOT/dossier_fatality_guard.py" --ledger "$SECURITY_LEDGER"; then
  notify_success "✅ Seguridad activa: ingreso >= 450.000€ confirmado y Dossier Fatality activado."
else
  notify_success "ℹ️ Guardia de seguridad ejecutada: pendiente evidencia de ingreso confirmado para activar Dossier Fatality."
fi

step "Galería 10/10"
echo "✅ Pipeline soberano finalizado sin errores de Bash."
