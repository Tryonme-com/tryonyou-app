#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"

BOT_NAME="${TRYONYOU_DEPLOY_BOT_NAME:-@tryonyou_deploy_bot}"
BOT_TOKEN="${TRYONYOU_DEPLOY_BOT_TOKEN:-${TELEGRAM_BOT_TOKEN:-${TELEGRAM_TOKEN:-}}}"
BOT_CHAT_ID="${TRYONYOU_DEPLOY_CHAT_ID:-${TELEGRAM_CHAT_ID:-7868120279}}"
BOT_TOKEN="${BOT_TOKEN//[[:space:]]/}"

DEFAULT_MESSAGE="chore: Supercommit_Max Oberkampf 75011 -> galeria web @CertezaAbsoluta @lo+erestu PCT/EP2025/067317 Bajo Protocolo de Soberanía V10 - Founder: Rubén"

notify_success() {
  local text="$1"
  if [[ -z "$BOT_TOKEN" ]]; then
    echo "[WARN] Telegram no configurado: omitiendo notificacion de exito."
    return 0
  fi

  if [[ -z "$BOT_CHAT_ID" ]]; then
    BOT_CHAT_ID="$(
      curl -sS "https://api.telegram.org/bot${BOT_TOKEN}/getUpdates" \
        | python3 -c 'import json,sys; d=json.load(sys.stdin); rs=d.get("result") or []; print(rs[-1]["message"]["chat"]["id"] if rs and rs[-1].get("message") and rs[-1]["message"].get("chat") else "")' 2>/dev/null || true
    )"
  fi

  if [[ -z "$BOT_CHAT_ID" ]]; then
    echo "[WARN] Telegram sin chat_id: no se pudo notificar."
    return 0
  fi

  local response
  response="$(curl -sS -X POST "https://api.telegram.org/bot${BOT_TOKEN}/sendMessage" \
    -d "chat_id=${BOT_CHAT_ID}" \
    --data-urlencode "text=${text}" \
    -d "parse_mode=HTML" || true)"

  if [[ "$response" != *'"ok":true'* ]]; then
    echo "[WARN] Telegram no confirmo entrega del mensaje."
  fi
}

ensure_required_stamps() {
  local input="$1"
  local out="$input"
  [[ "$out" == *"@CertezaAbsoluta"* ]] || out="${out} @CertezaAbsoluta"
  [[ "$out" == *"@lo+erestu"* ]] || out="${out} @lo+erestu"
  [[ "$out" == *"PCT/EP2025/067317"* ]] || out="${out} PCT/EP2025/067317"
  [[ "$out" == *"Bajo Protocolo de Soberanía V10 - Founder: Rubén"* ]] || out="${out} Bajo Protocolo de Soberanía V10 - Founder: Rubén"
  echo "$out"
}

push_with_retry() {
  local branch="$1"
  local attempt=1
  local delay=4
  while (( attempt <= 4 )); do
    if git push -u origin "$branch"; then
      return 0
    fi
    if (( attempt == 4 )); then
      return 1
    fi
    echo "[WARN] push fallido (intento ${attempt}/4). Reintentando en ${delay}s..."
    sleep "$delay"
    delay=$((delay * 2))
    attempt=$((attempt + 1))
  done
  return 1
}

COMMIT_MESSAGE="$(ensure_required_stamps "${1:-$DEFAULT_MESSAGE}")"
CURRENT_BRANCH="$(git rev-parse --abbrev-ref HEAD)"

echo "== Supercommit_Max =="
echo "Rama: ${CURRENT_BRANCH}"
echo "Bunker Oberkampf (75011) -> galeria web"

notify_success "✅ ${BOT_NAME} inicio Supercommit_Max en rama ${CURRENT_BRANCH}."

if [[ -f "${ROOT}/package.json" ]]; then
  echo "[1/4] Build de galeria web..."
  npm run build --if-present
fi

echo "[2/4] Stage de cambios..."
git add -A

if git diff --cached --quiet; then
  echo "[3/4] Sin cambios para commit."
else
  echo "[3/4] Commit..."
  git commit -m "$COMMIT_MESSAGE"
fi

echo "[4/4] Push..."
push_with_retry "$CURRENT_BRANCH"

notify_success "✅ ${BOT_NAME} exito Supercommit_Max: bunker 75011 sincronizado con galeria web en ${CURRENT_BRANCH}."
echo "Supercommit_Max completado."