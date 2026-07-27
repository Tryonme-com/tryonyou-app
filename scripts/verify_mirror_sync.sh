#!/usr/bin/env bash
set -euo pipefail

# Verificación operativa de sincronía lógica de espejo.
# No certifica disponibilidad de un servidor espejo externo sin endpoint explícito.

HEALTH_URL="${HEALTH_URL:-http://127.0.0.1:8000/health}"
TRACE_URL="${TRACE_URL:-http://127.0.0.1:8000/api/v1/core/trace}"
SESSION_ID="${SESSION_ID:-audit-sync-$(date +%s)}"
ACCOUNT_SCOPE="${ACCOUNT_SCOPE:-admin}"
RESPONSE_BODY_FILE="${RESPONSE_BODY_FILE:-$(mktemp)}"

cleanup() {
  rm -f "${RESPONSE_BODY_FILE}"
}
trap cleanup EXIT

require_http_ok() {
  local label="$1"
  local url="$2"
  shift 2
  local http_code
  http_code="$(curl -sS -o "${RESPONSE_BODY_FILE}" -w "%{http_code}" "$@" "${url}")"
  local body
  body="$(cat "${RESPONSE_BODY_FILE}")"

  echo "${label}_http_code=${http_code}"
  echo "${label}_payload=${body}"

  if [[ "${http_code}" =~ ^[45][0-9]{2}$ ]]; then
    echo "result=error (${label} respondió HTTP ${http_code})"
    exit 1
  fi

  if [[ ! "${http_code}" =~ ^[23][0-9]{2}$ ]]; then
    echo "result=error (${label} respondió HTTP ${http_code} — fuera de rango 2xx/3xx)"
    exit 1
  fi

  printf '%s' "${body}"
}

echo "== Mirror Sync Audit =="
echo "health_url=${HEALTH_URL}"
echo "trace_url=${TRACE_URL}"

health_json="$(require_http_ok "health" "${HEALTH_URL}")"

trace_payload="$(cat <<JSON
{
  "event_type": "mirror_sync_probe",
  "source": "sovereign_black_box_audit",
  "session_id": "${SESSION_ID}",
  "account_scope": "${ACCOUNT_SCOPE}",
  "meta": {
    "probe": true,
    "patent": "PCT/EP2025/067317"
  }
}
JSON
)"

trace_json="$(require_http_ok "trace" "${TRACE_URL}" \
  -X POST \
  -H "Content-Type: application/json" \
  -H "X-Jules-Session-Id: ${SESSION_ID}" \
  -H "X-Jules-Account-Scope: ${ACCOUNT_SCOPE}" \
  -d "${trace_payload}")"

echo "trace_response=${trace_json}"
echo "result=ok (sincronía lógica interna validada: health + trace)"
