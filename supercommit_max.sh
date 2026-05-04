#!/usr/bin/env bash
set -euo pipefail

FAST=false
DEPLOY=false
COMMIT_MSG="chore(bunker): Supercommit Max soberano"

for arg in "$@"; do
  case "$arg" in
    --fast) FAST=true ;;
    --deploy) DEPLOY=true ;;
    --msg=*) COMMIT_MSG="${arg#--msg=}" ;;
    --msg)
      echo "[supercommit_max] Use --msg='mensaje'." >&2
      exit 2
      ;;
    *)
      echo "[supercommit_max] Flag no reconocida: $arg" >&2
      exit 2
      ;;
  esac
done

if [[ "$FAST" != "true" ]]; then
  echo "[supercommit_max] Typecheck y build."
  npm run typecheck
  npm run build
fi

if [[ -z "$(git status --porcelain)" ]]; then
  echo "[supercommit_max] Nada que commitear."
  if [[ "$DEPLOY" == "true" ]]; then
    echo "[supercommit_max] deployall (puede desplegar si hay VERCEL_TOKEN)."
    npm run deployall
  fi
  exit 0
fi

mapfile -t CHANGED_FILES < <(
  {
    git diff --name-only
    git diff --name-only --cached
    git ls-files --others --exclude-standard
  } | sort -u | grep -Ev '(^|/)(node_modules|dist|\.vercel|__pycache__|logs)(/|$)|(^|/)\.env($|[./])|secret|token|credential|\.pem$|\.key$' | grep -E '(^|/)\.env\.example$|^[^[:space:]]+$' || true
)

if [[ "${#CHANGED_FILES[@]}" -eq 0 ]]; then
  echo "[supercommit_max] No hay cambios seguros para stage."
  exit 0
fi

git add -- "${CHANGED_FILES[@]}"

if git diff --cached --quiet; then
  echo "[supercommit_max] Stage vacío tras aplicar exclusiones."
  exit 0
fi

git commit -m "$(cat <<EOF
${COMMIT_MSG}

@CertezaAbsoluta @lo+erestu PCT/EP2025/067317 — Bajo Protocolo de Soberanía V10 - Founder: Rubén
EOF
)" --no-verify

if [[ "$DEPLOY" == "true" ]]; then
  echo "[supercommit_max] deployall (puede desplegar si hay VERCEL_TOKEN)."
  npm run deployall
fi

BRANCH="$(git branch --show-current)"
if [[ -z "$BRANCH" ]]; then
  echo "[supercommit_max] Rama no detectada; omito push." >&2
  exit 1
fi

git push -u origin "$BRANCH"

TOKEN="${TRYONYOU_DEPLOY_BOT_TOKEN:-${TELEGRAM_BOT_TOKEN:-${TELEGRAM_TOKEN:-}}}"
CHAT_ID="${TRYONYOU_DEPLOY_CHAT_ID:-${TELEGRAM_CHAT_ID:-}}"
if [[ -n "$TOKEN" && -n "$CHAT_ID" ]]; then
  curl -fsS -X POST "https://api.telegram.org/bot${TOKEN}/sendMessage" \
    -H "Content-Type: application/json" \
    --data "{\"chat_id\":\"${CHAT_ID}\",\"text\":\"TryOnYou Supercommit_Max OK: ${BRANCH} — PCT/EP2025/067317\"}" >/dev/null || \
    echo "[supercommit_max] Aviso: Telegram no confirmó la notificación." >&2
else
  echo "[supercommit_max] Sin token/chat de deploy en entorno; omito Telegram."
fi