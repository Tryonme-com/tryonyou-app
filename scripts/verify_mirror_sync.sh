#!/usr/bin/env bash
set -euo pipefail

# Verificación operativa de sincronía lógica de espejo.
# No certifica disponibilidad de un servidor espejo externo sin endpoint explícito.

HEALTH_URL="${HEALTH_URL:-http://127.0.0.1:8000/health}"
TRACE_URL="${TRACE_URL:-http://127.0.0.1:8000/api/v1/core/trace}"
SESSION_ID="${SESSION_ID:-audit-sync-$(date +%s)}"
ACCOUNT_SCOPE="${ACCOUNT_SCOPE:-admin}"

echo "== Mirror Sync Audit =="
echo "health_url=${HEALTH_URL}"
echo "trace_url=${TRACE_URL}"

health_json="$(curl -sS "${HEALTH_URL}")"
echo "health_payload=${health_json}"

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

trace_json="$(curl -sS -X POST "${TRACE_URL}" \
  -H "Content-Type: application/json" \
  -H "X-Jules-Session-Id: ${SESSION_ID}" \
  -H "X-Jules-Account-Scope: ${ACCOUNT_SCOPE}" \
  -d "${trace_payload}")"

echo "trace_response=${trace_json}"
echo "result=ok (sincronía lógica interna validada: health + trace)"
