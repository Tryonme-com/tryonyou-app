#!/usr/bin/env bash
set -euo pipefail

FAST=false
DEPLOY=false
USER_MSG=""

usage() {
  cat >&2 <<'EOF'
Uso: bash supercommit_max.sh [--fast] [--deploy] [--msg "mensaje"]

Hace validaciones, stage seguro, commit con sellos Pau y push a la rama actual.
No empuja a main ni versiona secretos/local build outputs.
EOF
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
    --msg|-m)
      if [[ $# -lt 2 ]]; then
        echo "[supercommit_max] Falta valor para $1" >&2
        exit 2
      fi
      USER_MSG="$2"
      shift 2
      ;;
    --help|-h)
      usage
      exit 0
      ;;
    *)
      if [[ -z "$USER_MSG" ]]; then
        USER_MSG="$1"
        shift
      else
        echo "[supercommit_max] Flag no reconocida: $1" >&2
        usage
        exit 2
      fi
      ;;
  esac
done

BRANCH="$(git branch --show-current)"
if [[ -z "$BRANCH" ]]; then
  echo "[supercommit_max] No hay rama git activa." >&2
  exit 2
fi
if [[ "$BRANCH" == "main" || "$BRANCH" == "master" ]]; then
  echo "[supercommit_max] Bloqueado: no se opera directamente sobre $BRANCH." >&2
  exit 2
fi

if [[ "$FAST" != "true" ]]; then
  echo "[supercommit_max] Typecheck y build."
  npm run typecheck
  npm run build
fi

mapfile -d '' DISCOVERED_PATHS < <(git ls-files --modified --others --deleted --exclude-standard -z)
CHANGED_PATHS=()
for path in "${DISCOVERED_PATHS[@]}"; do
  case "$path" in
    .env|.env.local|.env.*.local|.env.production|.env.development|.vercel/*|node_modules/*|dist/*|logs/*|.pytest_cache/*|__pycache__/*)
      ;;
    *)
      CHANGED_PATHS+=("$path")
      ;;
  esac
done
if ((${#CHANGED_PATHS[@]} > 0)); then
  git add -- "${CHANGED_PATHS[@]}"
fi

if git diff --cached --quiet; then
  echo "[supercommit_max] Nada que commitear."
  if [[ -n "${TRYONYOU_DEPLOY_BOT_TOKEN:-${TELEGRAM_BOT_TOKEN:-${TELEGRAM_TOKEN:-}}}" && -n "${TRYONYOU_DEPLOY_CHAT_ID:-${TELEGRAM_CHAT_ID:-}}" ]]; then
    python3 - <<'PY'
import os
import urllib.parse
import urllib.request

token = (os.getenv("TRYONYOU_DEPLOY_BOT_TOKEN") or os.getenv("TELEGRAM_BOT_TOKEN") or os.getenv("TELEGRAM_TOKEN") or "").strip()
chat_id = (os.getenv("TRYONYOU_DEPLOY_CHAT_ID") or os.getenv("TELEGRAM_CHAT_ID") or "").strip()
text = "[TryOnYou] Supercommit_Max: sin cambios pendientes; bunker sincronizado."
if token and chat_id:
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = urllib.parse.urlencode({"chat_id": chat_id, "text": text}).encode()
    try:
        urllib.request.urlopen(url, data=data, timeout=8)
    except Exception:
        pass
PY
  fi
  exit 0
fi

SUBJECT="${USER_MSG:-fix(bunker): sincronizar Supercommit Max y galeria}"

git commit -m "$(cat <<EOF
$SUBJECT

@CertezaAbsoluta @lo+erestu PCT/EP2025/067317 — Bajo Protocolo de Soberanía V10 - Founder: Rubén
EOF
)"

git push -u origin "$BRANCH"

if [[ "$DEPLOY" == "true" ]]; then
  echo "[supercommit_max] deployall (solo desplegara si hay VERCEL_TOKEN)."
  npm run deployall
fi

if [[ -n "${TRYONYOU_DEPLOY_BOT_TOKEN:-${TELEGRAM_BOT_TOKEN:-${TELEGRAM_TOKEN:-}}}" && -n "${TRYONYOU_DEPLOY_CHAT_ID:-${TELEGRAM_CHAT_ID:-}}" ]]; then
  python3 - <<'PY'
import os
import subprocess
import urllib.parse
import urllib.request

token = (os.getenv("TRYONYOU_DEPLOY_BOT_TOKEN") or os.getenv("TELEGRAM_BOT_TOKEN") or os.getenv("TELEGRAM_TOKEN") or "").strip()
chat_id = (os.getenv("TRYONYOU_DEPLOY_CHAT_ID") or os.getenv("TELEGRAM_CHAT_ID") or "").strip()
branch = subprocess.check_output(["git", "branch", "--show-current"], text=True).strip()
sha = subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], text=True).strip()
text = f"[TryOnYou] Supercommit_Max OK: {branch}@{sha}"
if token and chat_id:
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = urllib.parse.urlencode({"chat_id": chat_id, "text": text}).encode()
    try:
        urllib.request.urlopen(url, data=data, timeout=8)
    except Exception:
        pass
PY
fi