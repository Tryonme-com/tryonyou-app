#!/usr/bin/env bash
# supercommit_max v10.17
# Flujo soberano: add + commit + push con sellos obligatorios.
set -euo pipefail

FAST_MODE=0
DEPLOY_MODE=0
RAW_MSG=""

STAMP_CERT="@CertezaAbsoluta"
STAMP_ID="@lo+erestu"
STAMP_PATENT="PCT/EP2025/067317"
STAMP_PROTOCOL="Bajo Protocolo de Soberanía V10 - Founder: Rubén"
DEFAULT_MSG="OMEGA_DEPLOY: sincronización búnker Oberkampf 75011 con galería web"

usage() {
  cat <<'EOF'
Uso:
  bash supercommit_max.sh [--fast] [--deploy] [--msg "texto libre"]

Opciones:
  --fast      Omite build y tests.
  --deploy    Requiere VERCEL_TOKEN y habilita modo despliegue.
  --msg       Mensaje base del commit (sellos se auto-aplican).
  --help      Muestra esta ayuda.
EOF
}

append_stamp_if_missing() {
  local msg="$1"
  local stamp="$2"
  if [[ "$msg" != *"$stamp"* ]]; then
    printf '%s %s' "$msg" "$stamp"
  else
    printf '%s' "$msg"
  fi
}

build_commit_message() {
  local msg="${1:-$DEFAULT_MSG}"
  msg="$(append_stamp_if_missing "$msg" "$STAMP_CERT")"
  msg="$(append_stamp_if_missing "$msg" "$STAMP_ID")"
  msg="$(append_stamp_if_missing "$msg" "$STAMP_PATENT")"
  msg="$(append_stamp_if_missing "$msg" "$STAMP_PROTOCOL")"
  printf '%s\n' "$msg"
}

require_git_repo() {
  if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    echo "❌ Este directorio no es un repositorio git." >&2
    exit 1
  fi
}

maybe_run_quality_checks() {
  if [[ "$FAST_MODE" -eq 1 ]]; then
    echo "⚡ Modo --fast activo: se omite build/test."
    return
  fi

  echo "🧪 Vite production build"
  npm run build
  echo "🧪 Python tests"
  python3 -m unittest tests/test_supercommit_max.py
}

push_if_possible() {
  local branch
  branch="$(git branch --show-current)"

  if git remote get-url origin >/dev/null 2>&1; then
    if git rev-parse --abbrev-ref --symbolic-full-name '@{u}' >/dev/null 2>&1; then
      echo "🚀 Push a upstream origin/$branch..."
      git push -u origin "$branch"
    else
      echo "ℹ️ Sin upstream configurado (@{u}); intento establecer origin/$branch."
      if ! git push -u origin "$branch"; then
        echo "ℹ️ No se pudo establecer upstream remoto; se conserva commit local."
      fi
    fi
  else
    echo "ℹ️ Sin remote origin; omito push automático."
  fi
}

notify_success() {
  local token="${TRYONYOU_DEPLOY_BOT_TOKEN:-${TELEGRAM_BOT_TOKEN:-${TELEGRAM_TOKEN:-}}}"
  local chat="${TELEGRAM_CHAT_ID:-}"
  local bot_label="${TRYONYOU_DEPLOY_BOT_USERNAME:-@tryonyou_deploy_bot}"
  local branch msg status
  branch="$(git branch --show-current)"

  if [[ -z "$token" || -z "$chat" ]]; then
    echo "ℹ️ Telegram no configurado (TELEGRAM_BOT_TOKEN/TELEGRAM_CHAT_ID); éxito registrado solo en consola."
    return
  fi

  msg="✅ Supercommit_Max OK
Bot: ${bot_label}
Branch: ${branch}
Patente: ${STAMP_PATENT}
Protocolo: Soberanía V10"

  # Notificación best-effort: no bloquea el pipeline si Telegram no responde.
  status="$(curl -sS --max-time 20 -X POST "https://api.telegram.org/bot${token}/sendMessage" \
    -H "Content-Type: application/json" \
    -d "{\"chat_id\":\"${chat}\",\"text\":\"${msg}\"}" || true)"
  if [[ "$status" == *"\"ok\":true"* ]]; then
    echo "📣 Notificación enviada por Telegram."
  else
    echo "⚠️ No se pudo confirmar notificación Telegram."
  fi
}

maybe_handle_deploy_mode() {
  if [[ "$DEPLOY_MODE" -eq 0 ]]; then
    return
  fi
  if [[ -z "${VERCEL_TOKEN:-}" ]]; then
    echo "❌ --deploy requiere VERCEL_TOKEN en el entorno." >&2
    exit 2
  fi
  echo "☁️ Modo --deploy habilitado (token detectado)."
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
      if [[ $# -lt 2 ]]; then
        echo "❌ --msg requiere un texto." >&2
        exit 1
      fi
      RAW_MSG="$2"
      shift 2
      ;;
    --help|-h)
      usage
      exit 0
      ;;
    *)
      echo "❌ Opción no reconocida: $1" >&2
      usage
      exit 1
      ;;
  esac
done

require_git_repo
maybe_handle_deploy_mode
maybe_run_quality_checks

COMMIT_MSG="$(build_commit_message "$RAW_MSG")"

echo "📦 git add -A"
git add -A

if [[ -z "$(git status --porcelain)" ]]; then
  echo "ℹ️ Nada nuevo; sin commit."
  push_if_possible
  exit 0
fi

echo "📝 Commit soberano en curso..."
# Evita colisiones con escáneres de secretos que inspeccionan variables COMMIT_MSG.
env -u COMMIT_MSG git commit -m "$COMMIT_MSG"
echo "✅ Commit creado."

push_if_possible
notify_success
echo "👑 Supercommit_Max completado."