#!/usr/bin/env bash
# Audit_Watchdog — polling de estado compliance / tesorería (Búnker).
# Requiere: curl. Notificación: macOS (osascript) o Linux (notify-send).
#
# Uso:
#   export SYSTEM_TOKEN="..."   # obligatorio
#   ./scripts/audit_watchdog.sh
#
# Variables opcionales:
#   AUDIT_WATCHDOG_URL     default: https://api.tryonyou.app/v1/compliance/check_status
#   AUDIT_WATCHDOG_INTERVAL segundos entre polls (default 900 = 15 min)
#   AUDIT_WATCHDOG_MATCH   substring a buscar en el body (default RELEASED)
#
# Patente: PCT/EP2025/067317 — Bajo Protocolo de Soberanía V10 - Founder: Rubén

set -u

AUDIT_WATCHDOG_URL="${AUDIT_WATCHDOG_URL:-https://api.tryonyou.app/v1/compliance/check_status}"
AUDIT_WATCHDOG_INTERVAL="${AUDIT_WATCHDOG_INTERVAL:-900}"
AUDIT_WATCHDOG_MATCH="${AUDIT_WATCHDOG_MATCH:-RELEASED}"

notify_bunker() {
  local title="BÚNKER: Dinero liberado"
  local raw="${1:-Estado: ${AUDIT_WATCHDOG_MATCH}}"
  local msg
  msg="$(printf '%.500s' "$raw")"
  if command -v notify-send >/dev/null 2>&1; then
    notify-send "$title" "$msg"
  elif [[ "$(uname -s)" == "Darwin" ]]; then
    osascript -e "display notification \"${msg//\"/\\\"}\" with title \"${title//\"/\\\"}\""
  else
    printf '%s\n' "[$title] $msg" >&2
  fi
}

if [[ -z "${SYSTEM_TOKEN:-}" ]]; then
  echo "audit_watchdog: define SYSTEM_TOKEN en el entorno." >&2
  exit 1
fi

echo "audit_watchdog: URL=${AUDIT_WATCHDOG_URL} intervalo=${AUDIT_WATCHDOG_INTERVAL}s match=${AUDIT_WATCHDOG_MATCH}" >&2

while true; do
  ts="$(date -u +"%Y-%m-%dT%H:%M:%SZ" 2>/dev/null || date +"%Y-%m-%dT%H:%M:%SZ")"
  if ! body="$(curl -sS -f --max-time 60 -X GET "$AUDIT_WATCHDOG_URL" \
    -H "Authorization: Bearer ${SYSTEM_TOKEN}" \
    -H "Accept: application/json" 2>&1)"; then
    echo "[$ts] audit_watchdog: curl falló: $body" >&2
  elif echo "$body" | grep -q -- "$AUDIT_WATCHDOG_MATCH"; then
    echo "[$ts] audit_watchdog: coincidencia (${AUDIT_WATCHDOG_MATCH})" >&2
    notify_bunker "$body"
  else
    echo "[$ts] audit_watchdog: sin liberación aún" >&2
  fi
  sleep "$AUDIT_WATCHDOG_INTERVAL"
done
