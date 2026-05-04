#!/usr/bin/env bash
set -euo pipefail

FAST=false
DEPLOY=false
COMMIT_SUBJECT="chore(supercommit): sincronizar bunker y galeria web"

usage() {
  cat >&2 <<'EOF'
Uso: ./supercommit_max.sh [--fast] [--deploy] [--msg "asunto"]

  --fast      Omite typecheck/build previos.
  --deploy    Ejecuta npm run deployall tras push (despliega solo si hay VERCEL_TOKEN).
  --msg       Asunto del commit; se anaden sellos obligatorios automaticamente.
EOF
}

notify_success() {
  local message="$1"
  python3 - "$message" <<'PY'
import json
import os
import sys
import urllib.error
import urllib.request

message = sys.argv[1]
token = (
    os.environ.get("TRYONYOU_DEPLOY_BOT_TOKEN", "").strip()
    or os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
    or os.environ.get("TELEGRAM_TOKEN", "").strip()
)
chat_id = (
    os.environ.get("TRYONYOU_DEPLOY_CHAT_ID", "").strip()
    or os.environ.get("TELEGRAM_CHAT_ID", "").strip()
)
if not token or not chat_id:
    print("[supercommit_max] Notificacion omitida: falta token/chat en entorno.")
    raise SystemExit(0)

payload = json.dumps({"chat_id": chat_id, "text": message}).encode("utf-8")
request = urllib.request.Request(
    f"https://api.telegram.org/bot{token}/sendMessage",
    data=payload,
    headers={"Content-Type": "application/json"},
    method="POST",
)
try:
    with urllib.request.urlopen(request, timeout=20) as response:
        if response.status != 200:
            print(f"[supercommit_max] Telegram HTTP {response.status}", file=sys.stderr)
except (urllib.error.URLError, TimeoutError) as exc:
    print(f"[supercommit_max] Telegram no disponible: {exc}", file=sys.stderr)
PY
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
      if [[ $# -lt 2 ]]; then
        echo "[supercommit_max] --msg requiere un valor." >&2
        usage
        exit 2
      fi
      COMMIT_SUBJECT="$2"
      shift 2
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "[supercommit_max] Flag no reconocida: $1" >&2
      usage
      exit 2
      ;;
  esac
done

branch="$(git rev-parse --abbrev-ref HEAD)"
if [[ "$branch" == "HEAD" ]]; then
  echo "[supercommit_max] HEAD detached; abortando push seguro." >&2
  exit 1
fi

if [[ "$FAST" != "true" ]]; then
  echo "[supercommit_max] Typecheck y build."
  npm run typecheck
  npm run build
fi

mapfile -t changed_paths < <(git ls-files --modified --deleted --others --exclude-standard)
safe_paths=()
for path in "${changed_paths[@]}"; do
  case "$path" in
    .env|.env.*|*.env|*secret*|*Secret*|*token*|*Token*|node_modules/*|dist/*|logs/*)
      echo "[supercommit_max] Excluido del stage: $path"
      ;;
    *)
      safe_paths+=("$path")
      ;;
  esac
done

if [[ "${#safe_paths[@]}" -eq 0 ]]; then
  echo "[supercommit_max] Nada seguro que commitear."
  if [[ "$DEPLOY" == "true" ]]; then
    echo "[supercommit_max] deployall (puede desplegar si hay VERCEL_TOKEN)."
    npm run deployall
  fi
  notify_success "TryOnYou Supercommit_Max sin cambios en ${branch}."
  exit 0
fi

git add -- "${safe_paths[@]}"

if git diff --cached --quiet; then
  echo "[supercommit_max] Stage vacio tras filtros."
  exit 0
fi

git commit -m "$(cat <<EOF
${COMMIT_SUBJECT}

@CertezaAbsoluta @lo+erestu PCT/EP2025/067317
Bajo Protocolo de Soberanía V10 - Founder: Rubén
EOF
)"

git push -u origin "$branch"

if [[ "$DEPLOY" == "true" ]]; then
  echo "[supercommit_max] deployall (puede desplegar si hay VERCEL_TOKEN)."
  npm run deployall
fi

notify_success "TryOnYou Supercommit_Max OK en ${branch}: ${COMMIT_SUBJECT}"