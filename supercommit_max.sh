#!/usr/bin/env bash
set -euo pipefail

FAST=false
DEPLOY=false
CUSTOM_MSG=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --fast) FAST=true ;;
    --deploy) DEPLOY=true ;;
    --msg)
      shift
      if [[ $# -eq 0 ]]; then
        echo "[supercommit_max] --msg requiere un valor." >&2
        exit 2
      fi
      CUSTOM_MSG="$1"
      ;;
    *)
      echo "[supercommit_max] Flag no reconocida: $1" >&2
      exit 2
      ;;
  esac
  shift
done

ROOT="$(git rev-parse --show-toplevel)"
cd "$ROOT"

notify_success() {
  local text="$1"
  local token="${TRYONYOU_DEPLOY_BOT_TOKEN:-${TELEGRAM_BOT_TOKEN:-${TELEGRAM_TOKEN:-}}}"
  local chat="${TRYONYOU_DEPLOY_CHAT_ID:-${TELEGRAM_CHAT_ID:-}}"

  if [[ -z "$token" || -z "$chat" ]]; then
    echo "[supercommit_max] Notificacion omitida: falta TRYONYOU_DEPLOY_BOT_TOKEN/TELEGRAM_BOT_TOKEN o TRYONYOU_DEPLOY_CHAT_ID/TELEGRAM_CHAT_ID."
    return 0
  fi

  curl -fsS "https://api.telegram.org/bot${token}/sendMessage" \
    -H "Content-Type: application/json" \
    --data "$(python3 - "$chat" "$text" <<'PY'
import json
import sys

print(json.dumps({"chat_id": sys.argv[1], "text": sys.argv[2]}))
PY
)" >/dev/null
}

if [[ "$FAST" != "true" ]]; then
  echo "[supercommit_max] Typecheck y build."
  npm run typecheck
  npm run build
fi

stage_safe_paths() {
  local path
  while IFS= read -r -d '' path; do
    case "$path" in
      .env|.env.local|.env.*.local|*/.env|*/.env.local|*/.env.*.local|node_modules/*|dist/*|*.pem|*.key|*.log|*secret*|*token*)
        if [[ "$path" != ".env.example" && "$path" != */.env.example ]]; then
          echo "[supercommit_max] Excluido del stage seguro: $path"
          continue
        fi
        ;;
    esac
    git add -- "$path"
  done < <(git ls-files -m -o --exclude-standard -z)

  while IFS= read -r -d '' path; do
    git add -- "$path"
  done < <(git ls-files -d -z)
}

stage_safe_paths

if git diff --cached --quiet; then
  echo "[supercommit_max] Nada que commitear."
  notify_success "TryOnYou Supercommit_Max: rama limpia en $(git branch --show-current)."
  exit 0
fi

if [[ -z "$CUSTOM_MSG" ]]; then
  CUSTOM_MSG="chore(supercommit): sincronizar bunker y galeria web"
fi

git commit -m "$(cat <<EOF
${CUSTOM_MSG}

@CertezaAbsoluta @lo+erestu PCT/EP2025/067317 — Bajo Protocolo de Soberanía V10 - Founder: Rubén
EOF
)"

BRANCH="$(git branch --show-current)"
if [[ -z "$BRANCH" ]]; then
  echo "[supercommit_max] No hay rama git activa; push cancelado." >&2
  exit 2
fi

git push -u origin "$BRANCH"
notify_success "TryOnYou Supercommit_Max: commit y push OK en ${BRANCH}."

if [[ "$DEPLOY" == "true" ]]; then
  if [[ -z "${VERCEL_TOKEN:-}" ]]; then
    echo "[supercommit_max] VERCEL_TOKEN no definido; deploy cancelado despues del push seguro." >&2
    exit 3
  fi
  echo "[supercommit_max] deployall (puede desplegar si hay VERCEL_TOKEN)."
  npm run deployall
  notify_success "TryOnYou Supercommit_Max: deployall ejecutado en ${BRANCH}."
fi