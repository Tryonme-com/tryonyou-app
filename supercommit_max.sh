#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FAST=false
DEPLOY=false
CUSTOM_MESSAGE="chore(supercommit): sincronizar bunker Oberkampf y galeria"

usage() {
  cat <<'EOF'
Uso: ./Supercommit_Max [--fast] [--deploy] [--msg "mensaje"]

Ejecuta validaciones, crea un commit seguro en la rama activa y hace push no
destructivo a origin/<rama>. No empuja a main salvo que esa sea la rama activa.
EOF
}

notify_success() {
  local message="$1"
  local token="${TRYONYOU_DEPLOY_BOT_TOKEN:-${TELEGRAM_BOT_TOKEN:-${TELEGRAM_TOKEN:-}}}"
  local chat_id="${TRYONYOU_DEPLOY_CHAT_ID:-${TELEGRAM_CHAT_ID:-}}"

  token="$(printf '%s' "$token" | tr -d '[:space:]')"
  chat_id="$(printf '%s' "$chat_id" | tr -d '[:space:]')"

  if [[ -z "$token" || -z "$chat_id" ]]; then
    echo "[supercommit_max] Telegram omitido: falta token o chat id en entorno."
    return 0
  fi

  curl -fsS \
    --request POST \
    --url "https://api.telegram.org/bot${token}/sendMessage" \
    --header "Content-Type: application/json" \
    --data "$(python3 - "$chat_id" "$message" <<'PY'
import json
import sys

print(json.dumps({"chat_id": sys.argv[1], "text": sys.argv[2]}))
PY
)" >/dev/null || {
    echo "[supercommit_max] Telegram no confirmado; continuar sin exponer token." >&2
    return 0
  }
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --fast)
      FAST=true
      shift
      ;;
    --deploy)
      DEPLOY=true
      shift
      ;;
    --msg)
      if [[ $# -lt 2 || -z "${2:-}" ]]; then
        echo "[supercommit_max] --msg requiere texto." >&2
        exit 2
      fi
      CUSTOM_MESSAGE="$2"
      shift 2
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "[supercommit_max] Flag no reconocida: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
done

cd "$ROOT"

if [[ "$FAST" != "true" ]]; then
  echo "[supercommit_max] Typecheck y build."
  npm run typecheck
  npm run build
fi

branch="$(git branch --show-current)"
if [[ -z "$branch" ]]; then
  echo "[supercommit_max] Rama detached; cancelo commit/push seguro." >&2
  exit 3
fi

if [[ -z "$(git status --porcelain)" ]]; then
  echo "[supercommit_max] Nada que commitear."
  notify_success "TryOnYou Supercommit_Max OK: bunker Oberkampf sincronizado, galeria sin cambios pendientes (${branch})."
else
  git add -u -- .
  git reset -q -- .env .env.* dist node_modules build '*.log' 2>/dev/null || true

  safe_untracked=()
  while IFS= read -r -d '' path; do
    case "$path" in
      .env|.env.*|node_modules/*|dist/*|build/*|*.log)
        continue
        ;;
    esac
    safe_untracked+=("$path")
  done < <(git ls-files --others --exclude-standard -z)

  if [[ "${#safe_untracked[@]}" -gt 0 ]]; then
    git add -- "${safe_untracked[@]}"
  fi

  git commit -m "$(cat <<EOF
${CUSTOM_MESSAGE}

@CertezaAbsoluta @lo+erestu PCT/EP2025/067317 — Bajo Protocolo de Soberanía V10 - Founder: Rubén
EOF
)"

  git push -u origin "$branch"
  notify_success "TryOnYou Supercommit_Max OK: bunker Oberkampf 75011 sincronizado con galeria web (${branch})."
fi

if [[ "$DEPLOY" == "true" ]]; then
  if [[ -z "${VERCEL_TOKEN:-}" ]]; then
    echo "[supercommit_max] Deploy omitido: VERCEL_TOKEN no esta configurado."
  else
    echo "[supercommit_max] deployall con VERCEL_TOKEN presente."
    npm run deployall
  fi
fi