#!/usr/bin/env bash
# supercommit_max — add + commit + push (+deploy opcional) con sellos TryOnYou.
set -euo pipefail

readonly STAMP_CERTEZA="@CertezaAbsoluta"
readonly STAMP_ERES_TU="@lo+erestu"
readonly STAMP_PATENTE="PCT/EP2025/067317"
readonly STAMP_PROTOCOLO="Bajo Protocolo de Soberanía V10 - Founder: Rubén"
readonly DEFAULT_TITLE="OMEGA_DEPLOY"

FAST_MODE=0
DEPLOY_MODE=0
CUSTOM_MSG=""

usage() {
  cat <<'EOF'
Uso:
  bash supercommit_max.sh [--fast] [--deploy] [--msg "mensaje custom"]

Opciones:
  --fast        Omite build y tests.
  --deploy      Ejecuta deploy en Vercel (requiere VERCEL_TOKEN).
  --msg         Mensaje custom de commit (los sellos se auto-anexan si faltan).
  -h, --help    Muestra esta ayuda.
EOF
}

notify_success() {
  local stage="$1"
  local details="$2"
  local token="${TRYONYOU_DEPLOY_BOT_TOKEN:-${TELEGRAM_BOT_TOKEN:-${TELEGRAM_TOKEN:-}}}"
  local chat_id="${TRYONYOU_DEPLOY_CHAT_ID:-${TELEGRAM_CHAT_ID:-}}"
  if [[ -z "$token" || -z "$chat_id" ]]; then
    return 0
  fi

  local text
  text="✅ Supercommit_Max: ${stage}"$'\n'"${details}"
  curl -sS --max-time 20 \
    -X POST "https://api.telegram.org/bot${token}/sendMessage" \
    --data-urlencode "chat_id=${chat_id}" \
    --data-urlencode "text=${text}" \
    --data-urlencode "parse_mode=HTML" >/dev/null || true
}

append_stamp_if_missing() {
  local msg="$1"
  local stamp="$2"
  if [[ "$msg" != *"$stamp"* ]]; then
    msg="${msg} ${stamp}"
  fi
  printf '%s' "$msg"
}

with_required_stamps() {
  local msg="$1"
  msg="$(append_stamp_if_missing "$msg" "$STAMP_CERTEZA")"
  msg="$(append_stamp_if_missing "$msg" "$STAMP_ERES_TU")"
  msg="$(append_stamp_if_missing "$msg" "$STAMP_PATENTE")"
  msg="$(append_stamp_if_missing "$msg" "$STAMP_PROTOCOLO")"
  printf '%s\n' "$msg"
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --fast)
      FAST_MODE=1
      shift
      ;;
    --deploy)
      DEPLOY_MODE=1
      shift
      ;;
    --msg)
      shift
      if [[ $# -eq 0 ]]; then
        echo "❌ --msg requiere un valor." >&2
        exit 1
      fi
      CUSTOM_MSG="$1"
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "❌ Opción no reconocida: $1" >&2
      usage >&2
      exit 1
      ;;
  esac
done

if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "❌ Debes ejecutar supercommit_max.sh dentro de un repositorio git." >&2
  exit 1
fi

COMMIT_TITLE="${CUSTOM_MSG:-$DEFAULT_TITLE}"
COMMIT_MESSAGE_TEXT="$(with_required_stamps "$COMMIT_TITLE")"

if [[ "$FAST_MODE" -eq 0 ]]; then
  echo "🧪 Vite production build"
  npm run build

  echo "🧪 Python tests"
  python3 -m unittest tests/test_supercommit_max.py
fi

git add -A
if git diff --cached --quiet; then
  echo "ℹ️ nada nuevo, sin commit."
else
  # Evita colisión con secretos exportados como COMMIT_MSG en el entorno CI/agent.
  unset COMMIT_MSG || true
  git commit -m "$COMMIT_MESSAGE_TEXT"
  echo "✅ Commit creado."
  notify_success "commit" "Commit registrado en $(git rev-parse --abbrev-ref HEAD)."
fi

if git rev-parse --abbrev-ref --symbolic-full-name '@{u}' >/dev/null 2>&1; then
  git push
  echo "✅ Push completado."
  notify_success "push" "Push ejecutado correctamente."
else
  echo "ℹ️ No hay upstream configurado (@{u}); se omite push."
fi

if [[ "$DEPLOY_MODE" -eq 1 ]]; then
  if [[ -z "${VERCEL_TOKEN:-}" ]]; then
    echo "❌ ERROR: falta VERCEL_TOKEN para --deploy." >&2
    exit 1
  fi
  echo "🚀 Deploy Vercel en curso..."
  vercel deploy --prod --yes --token="$VERCEL_TOKEN"
  echo "✅ Deploy completado."
  notify_success "deploy" "Deploy Vercel finalizado."
fi