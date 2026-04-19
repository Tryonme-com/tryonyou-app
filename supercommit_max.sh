#!/usr/bin/env bash
# supercommit_max.sh — flujo soberano de commit/push/despliegue TryOnYou.
set -euo pipefail

FAST_MODE=0
DEPLOY_MODE=0
SKIP_NOTIFY=0
CUSTOM_MSG=""

STAMP_CERTEZA="@CertezaAbsoluta"
STAMP_PAU="@lo+erestu"
STAMP_PATENT="PCT/EP2025/067317"
STAMP_PROTOCOL="Bajo Protocolo de Soberanía V10 - Founder: Rubén"
DEFAULT_PREFIX="OMEGA_DEPLOY"

usage() {
  cat <<'EOF'
Uso:
  bash supercommit_max.sh [--fast] [--deploy] [--msg "texto"] [--skip-notify]

Flags:
  --fast         Omite build y pruebas de Python.
  --deploy       Ejecuta despliegue Vercel tras el commit/push (requiere VERCEL_TOKEN).
  --msg          Mensaje de commit base; se auto-completan sellos obligatorios.
  --skip-notify  No enviar notificaciones Telegram.
EOF
}

append_stamp_if_missing() {
  local message="$1"
  local stamp="$2"
  if [[ "$message" == *"$stamp"* ]]; then
    printf '%s' "$message"
  else
    printf '%s %s' "$message" "$stamp"
  fi
}

compose_commit_message() {
  local base="$1"
  local msg="$base"
  msg="$(append_stamp_if_missing "$msg" "$STAMP_CERTEZA")"
  msg="$(append_stamp_if_missing "$msg" "$STAMP_PAU")"
  msg="$(append_stamp_if_missing "$msg" "$STAMP_PATENT")"
  msg="$(append_stamp_if_missing "$msg" "$STAMP_PROTOCOL")"
  printf '%s\n' "$msg"
}

notify_success() {
  local text="$1"
  local token="${TRYONYOU_DEPLOY_BOT_TOKEN:-${TELEGRAM_BOT_TOKEN:-${TELEGRAM_TOKEN:-}}}"
  local chat="${TRYONYOU_DEPLOY_CHAT_ID:-${TELEGRAM_CHAT_ID:-}}"
  local bot_name="${TRYONYOU_DEPLOY_BOT_NAME:-@tryonyou_deploy_bot}"
  local url

  if [[ "$SKIP_NOTIFY" -eq 1 ]]; then
    return 0
  fi

  if [[ "$bot_name" != "@tryonyou_deploy_bot" ]]; then
    echo "⚠️ TRYONYOU_DEPLOY_BOT_NAME distinto al esperado (@tryonyou_deploy_bot)." >&2
  fi

  if [[ -z "$token" || -z "$chat" ]]; then
    echo "ℹ️ Sin token/chat de Telegram; notificación omitida." >&2
    return 0
  fi

  url="https://api.telegram.org/bot${token}/sendMessage"
  if ! curl -fsS -X POST "$url" \
    --data-urlencode "chat_id=${chat}" \
    --data-urlencode "text=${text}" >/dev/null; then
    echo "⚠️ No se pudo enviar notificación Telegram." >&2
    return 1
  fi

  return 0
}

has_upstream() {
  git rev-parse --abbrev-ref --symbolic-full-name "@{u}" >/dev/null 2>&1
}

run_pipeline_checks() {
  if [[ "$FAST_MODE" -eq 1 ]]; then
    echo "⚡ Modo fast activo: sin build ni test."
    return 0
  fi

  echo "▶ Vite production build"
  npm run build

  echo "▶ Python tests"
  python3 -m unittest -q tests/test_supercommit_max.py
}

run_deploy() {
  if [[ "$DEPLOY_MODE" -ne 1 ]]; then
    return 0
  fi

  if [[ -z "${VERCEL_TOKEN:-}" ]]; then
    echo "❌ --deploy requiere VERCEL_TOKEN." >&2
    return 1
  fi

  if ! command -v vercel >/dev/null 2>&1; then
    echo "❌ Vercel CLI no disponible." >&2
    return 1
  fi

  echo "🚀 Despliegue Vercel producción en curso..."
  vercel deploy --prod --yes --token="$VERCEL_TOKEN"
  notify_success "✅ Supercommit_Max deploy OK (Oberkampf 75011 ↔ galería web)."
}

validate_deploy_requirements() {
  if [[ "$DEPLOY_MODE" -ne 1 ]]; then
    return 0
  fi

  if [[ -z "${VERCEL_TOKEN:-}" ]]; then
    echo "❌ --deploy requiere VERCEL_TOKEN." >&2
    return 1
  fi
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --fast)
      FAST_MODE=1
      ;;
    --deploy)
      DEPLOY_MODE=1
      ;;
    --skip-notify)
      SKIP_NOTIFY=1
      ;;
    --msg)
      shift
      if [[ $# -eq 0 ]]; then
        echo "❌ --msg requiere un valor." >&2
        exit 2
      fi
      CUSTOM_MSG="$1"
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "❌ Flag no reconocida: $1" >&2
      usage
      exit 2
      ;;
  esac
  shift
done

if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "❌ Debes ejecutar supercommit_max dentro de un repositorio git." >&2
  exit 1
fi

validate_deploy_requirements
run_pipeline_checks

timestamp="$(date +%Y-%m-%d_%H-%M-%S)"
base_message="${CUSTOM_MSG:-${DEFAULT_PREFIX} ${timestamp}}"
commit_message="$(compose_commit_message "$base_message")"

git add -A

if git diff --cached --quiet; then
  echo "ℹ️ Nada nuevo para commit (sin commit)."
  if has_upstream; then
    echo "ℹ️ Upstream detectado; repositorio limpio."
  else
    echo "ℹ️ Sin upstream configurado (@{u})."
  fi
  notify_success "✅ Supercommit_Max OK sin cambios (repositorio limpio)."
  exit 0
fi

git commit -m "$commit_message"
notify_success "✅ Commit soberano creado: ${base_message}"

if has_upstream; then
  echo "📡 Push a upstream..."
  git push
  notify_success "✅ Push soberano completado."
else
  branch_name="$(git rev-parse --abbrev-ref HEAD)"
  echo "ℹ️ Sin upstream para la rama '${branch_name}' (@{u})."
  echo "   Ejecuta: git push -u origin ${branch_name}"
fi

run_deploy

echo "🏛️ Supercommit_Max completado."