#!/usr/bin/env bash
# supercommit_max — add + commit con sellos TryOnYou; push opcional por variable de entorno.
# Uso:
#   ./supercommit_max.sh "Tu mensaje de commit @CertezaAbsoluta @lo+erestu PCT/EP2025/067317"
#   SUPERCOMMIT_PUSH=1 ./supercommit_max.sh "Tu mensaje de commit @CertezaAbsoluta @lo+erestu PCT/EP2025/067317"
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"

REQUIRED_SEAL_1="@CertezaAbsoluta"
REQUIRED_SEAL_2="@lo+erestu"
REQUIRED_SEAL_3="PCT/EP2025/067317"

MESSAGE="${1:-}"
if [[ -z "$MESSAGE" ]]; then
  echo "Uso: ./supercommit_max.sh \"Tu mensaje de commit ${REQUIRED_SEAL_1} ${REQUIRED_SEAL_2} ${REQUIRED_SEAL_3}\"" >&2
  exit 1
fi

if [[ "$MESSAGE" != *"$REQUIRED_SEAL_1"* ]] || [[ "$MESSAGE" != *"$REQUIRED_SEAL_2"* ]] || [[ "$MESSAGE" != *"$REQUIRED_SEAL_3"* ]]; then
  echo "❌ El mensaje debe incluir: ${REQUIRED_SEAL_1}, ${REQUIRED_SEAL_2} y ${REQUIRED_SEAL_3}" >&2
  exit 2
fi

git add -A

if git diff --cached --quiet; then
  echo "ℹ️ Sin cambios para commit."
  exit 0
fi

git commit -m "$MESSAGE"
echo "✅ Commit creado."

if [[ "${SUPERCOMMIT_PUSH:-0}" == "1" ]]; then
  BRANCH="$(git rev-parse --abbrev-ref HEAD)"
  if [[ "${SUPERCOMMIT_FORCE_PUSH:-0}" == "1" ]]; then
    git push --force origin "$BRANCH"
  else
    git push origin "$BRANCH"
  fi
  echo "🚀 Push completado en $BRANCH."
else
  echo "ℹ️ Push no ejecutado (activa SUPERCOMMIT_PUSH=1 para empujar)."
fi
