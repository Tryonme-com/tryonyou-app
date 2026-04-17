#!/usr/bin/env bash
# Supercommit_Max TryOnYou:
# - valida sintaxis bash
# - sincroniza bunker (repo local) con galeria web (build Vite)
# - commit + push con sellos de soberanía
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"

if [[ "${1:-}" == "-h" || "${1:-}" == "--help" ]]; then
  echo "Uso: ./supercommit_max.sh [mensaje_commit]"
  exit 0
fi

BRANCH="$(git rev-parse --abbrev-ref HEAD)"
DEFAULT_MESSAGE="chore: Supercommit_Max sincroniza Oberkampf 75011 con galería web @CertezaAbsoluta @lo+erestu PCT/EP2025/067317 Bajo Protocolo de Soberanía V10 - Founder: Rubén"
COMMIT_MESSAGE="${1:-$DEFAULT_MESSAGE}"

echo "[SUPERCOMMIT_MAX] Rama activa: $BRANCH"
echo "Verificando sintaxis bash..."
bash -n "$0"

if [[ -f "package.json" ]]; then
  echo "Build de galeria web (npm run build --if-present)..."
  npm run build --if-present
else
  echo "package.json no encontrado; se omite build."
fi

echo "Preparando commit..."
git add -A
if git diff --cached --quiet; then
  echo "No hay cambios para commitear."
  exit 0
fi

git commit -m "$COMMIT_MESSAGE"
echo "Push soberano a origin/$BRANCH"
git push -u origin "$BRANCH"
echo "Supercommit_Max completado."