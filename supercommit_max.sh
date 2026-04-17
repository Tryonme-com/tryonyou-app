#!/usr/bin/env bash
# Supercommit Max TryOnYou:
# - sincroniza búnker local con la galería web (build opcional)
# - aplica sellos de commit obligatorios
# - hace push en la rama actual (sin force)
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT_DIR"

REQUIRED_PROTOCOL="Bajo Protocolo de Soberanía V10 - Founder: Rubén"

if [[ "${1:-}" == "" ]]; then
  echo "Uso:"
  echo "  ./supercommit_max.sh \"mensaje base del commit\""
  echo
  echo "Opciones por entorno:"
  echo "  SUPERCOMMIT_SKIP_BUILD=1   # omite npm run build"
  exit 1
fi

BASE_MESSAGE="$1"
COMMIT_MESSAGE="$BASE_MESSAGE"

if [[ "$COMMIT_MESSAGE" != *"@CertezaAbsoluta"* ]]; then
  COMMIT_MESSAGE="$COMMIT_MESSAGE @CertezaAbsoluta"
fi
if [[ "$COMMIT_MESSAGE" != *"@lo+erestu"* ]]; then
  COMMIT_MESSAGE="$COMMIT_MESSAGE @lo+erestu"
fi
if [[ "$COMMIT_MESSAGE" != *"PCT/EP2025/067317"* ]]; then
  COMMIT_MESSAGE="$COMMIT_MESSAGE PCT/EP2025/067317"
fi
if [[ "$COMMIT_MESSAGE" != *"$REQUIRED_PROTOCOL"* ]]; then
  COMMIT_MESSAGE="$COMMIT_MESSAGE $REQUIRED_PROTOCOL"
fi

echo "🏛️ Supercommit Max: sincronizando búnker y galería web..."

if [[ -f package.json && "${SUPERCOMMIT_SKIP_BUILD:-0}" != "1" ]]; then
  echo "🧪 Ejecutando build de galería web..."
  npm run build
else
  echo "ℹ️ Build omitido (SUPERCOMMIT_SKIP_BUILD=1 o package.json ausente)."
fi

git add -A

if git diff --staged --quiet; then
  echo "ℹ️ No hay cambios para commitear."
  exit 0
fi

CURRENT_BRANCH="$(git rev-parse --abbrev-ref HEAD)"
if [[ "$CURRENT_BRANCH" == "HEAD" ]]; then
  echo "❌ Estado detached HEAD. Cambia a una rama antes de continuar."
  exit 2
fi

echo "✍️ Commit con sellos requeridos..."
git commit -m "$COMMIT_MESSAGE"

echo "🚀 Push a origin/$CURRENT_BRANCH"
git push -u origin "$CURRENT_BRANCH"

echo "✅ Supercommit Max completado."