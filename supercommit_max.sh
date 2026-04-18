#!/usr/bin/env bash
# supercommit_max.sh — flujo soberano de commit/push con sellos obligatorios
# y notificación opcional por Telegram al bot de despliegue.
#
# Uso:
#   ./supercommit_max.sh
#   ./supercommit_max.sh --fast
#   ./supercommit_max.sh --msg "mensaje custom"
#   ./supercommit_max.sh --deploy
#
# Sellos obligatorios en commit:
#   @CertezaAbsoluta @lo+erestu PCT/EP2025/067317
#   Bajo Protocolo de Soberanía V10 - Founder: Rubén

set -euo pipefail

DEFAULT_TITLE="OMEGA_DEPLOY: sincronización búnker Oberkampf 75011 con galería web"
STAMP_C="@CertezaAbsoluta"
STAMP_L="@lo+erestu"
STAMP_P="PCT/EP2025/067317"
STAMP_PROTOCOL="Bajo Protocolo de Soberanía V10 - Founder: Rubén"

FAST_MODE=false
DEPLOY_MODE=false
COMMIT_TITLE="$DEFAULT_TITLE"

TELEGRAM_CHAT_ID_DEFAULT='7868120279'

usage() {
  cat <<'USAGE'
Usage: bash supercommit_max.sh [options]

Options:
  --fast              Salta tests/build, solo git + push.
  --deploy            Ejecuta scripts/deployall.sh tras push (requiere VERCEL_TOKEN).
  --msg "texto"       Título del commit (los sellos se añaden automáticamente si faltan).
  -h, --help          Muestra esta ayuda.
USAGE
}

append_stamp_if_missing() {
  local input="$1"
  local token="$2"
  if [[ "$input" != *"$token"* ]]; then
    input+=" $token"
  fi
  printf '%s' "$input"
}

build_commit_message() {
  local msg="$1"
  msg="$(append_stamp_if_missing "$msg" "$STAMP_C")"
  msg="$(append_stamp_if_missing "$msg" "$STAMP_L")"
  msg="$(append_stamp_if_missing "$msg" "$STAMP_P")"
  msg="$(append_stamp_if_missing "$msg" "$STAMP_PROTOCOL")"
  printf '%s' "$msg"
}

notify_telegram_success() {
  local summary="$1"
  local token="${TELEGRAM_BOT_TOKEN:-${TELEGRAM_TOKEN:-}}"
  local chat_id="${TELEGRAM_CHAT_ID:-$TELEGRAM_CHAT_ID_DEFAULT}"

  if [[ -z "$token" || -z "$chat_id" ]]; then
    echo "[supercommit] Telegram omitido: token/chat_id ausentes."
    return 0
  fi

  local payload
  payload="$(python3 - "$chat_id" "$summary" <<'PYJSON'
import json,sys
print(json.dumps({"chat_id": sys.argv[1], "text": sys.argv[2]}))
PYJSON
)"

  local url="https://api.telegram.org/bot${token}/sendMessage"
  if command -v curl >/dev/null 2>&1; then
    curl -sS -X POST "$url" -H 'Content-Type: application/json' -d "$payload" >/dev/null || true
  elif command -v python3 >/dev/null 2>&1; then
    python3 - "$url" "$payload" <<'PYREQ' >/dev/null 2>&1 || true
import json,sys,urllib.request
req=urllib.request.Request(sys.argv[1],data=sys.argv[2].encode(),headers={"Content-Type":"application/json"})
urllib.request.urlopen(req,timeout=20).read()
PYREQ
  fi
}

ensure_repo() {
  git rev-parse --is-inside-work-tree >/dev/null 2>&1 || {
    echo "❌ No estás dentro de un repositorio git." >&2
    exit 2
  }
}

run_quality_checks() {
  if $FAST_MODE; then
    echo "[supercommit] --fast activo: se omiten build/tests."
    return 0
  fi

  if [[ -f package.json ]]; then
    echo "[supercommit] Ejecutando Vite production build..."
    npm run build
  fi

  if [[ -d tests ]]; then
    echo "[supercommit] Ejecutando Python tests..."
    python3 -m unittest discover -s tests -p 'test_*.py'
  fi
}

main() {
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --fast)
        FAST_MODE=true
        shift
        ;;
      --deploy)
        DEPLOY_MODE=true
        shift
        ;;
      --msg)
        [[ $# -lt 2 ]] && { echo "❌ --msg requiere argumento." >&2; exit 2; }
        COMMIT_TITLE="$2"
        shift 2
        ;;
      -h|--help)
        usage
        exit 0
        ;;
      *)
        echo "❌ Opción no reconocida: $1" >&2
        usage
        exit 2
        ;;
    esac
  done

  ensure_repo
  local branch
  branch="$(git branch --show-current)"
  if [[ -z "$branch" ]]; then
    echo "❌ Rama no detectada." >&2
    exit 2
  fi

  local final_msg
  final_msg="$(build_commit_message "$COMMIT_TITLE")"

  if $DEPLOY_MODE && [[ -z "${VERCEL_TOKEN:-}" ]]; then
    echo "❌ --deploy requiere VERCEL_TOKEN en entorno." >&2
    exit 1
  fi

  run_quality_checks

  git add .
  if git diff --cached --quiet; then
    echo "ℹ️  Nada nuevo para commit."
    if ! git rev-parse --abbrev-ref '@{u}' >/dev/null 2>&1; then
      echo "ℹ️  Sin upstream configurado (@{u})."
      return 0
    fi

    if git push; then
      notify_telegram_success "✅ @tryonyou_deploy_bot: éxito de sincronización (sin cambios nuevos) en rama ${branch}."
      return 0
    fi

    echo "⚠️ Push falló aunque no había cambios; revisa remote." >&2
    return 1
  fi

  git commit -m "$final_msg"

  if ! git rev-parse --abbrev-ref '@{u}' >/dev/null 2>&1; then
    git push -u origin "$branch"
  else
    git push
  fi

  if $DEPLOY_MODE; then
    if [[ -x scripts/deployall.sh ]]; then
      bash scripts/deployall.sh
    else
      echo "⚠️ scripts/deployall.sh no encontrado; se omite deploy." >&2
    fi
  fi

  notify_telegram_success "✅ @tryonyou_deploy_bot: Supercommit_Max completado en ${branch}."
  echo "✅ Supercommit_Max completado en rama ${branch}."
}

main "$@"
