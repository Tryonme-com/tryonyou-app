#!/usr/bin/env bash
# TRYONYOU–ABVETOS–ULTRA–PLUS–ULTIMATUM — SuperCommit MAX
# Agente 70: PURGE_AND_SYNC + sellos + push.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"

echo "🦚 TRYONYOU–ABVETOS–ULTRA–PLUS–ULTIMATUM — SuperCommit MAX"

# ── 1. Cambiar a main y actualizar ────────────────────────────────────────────
echo "📌 Cambiando a branch main..."
git checkout main

echo "📥 Actualizando desde origin main..."
if ! git pull origin main --ff-only; then
  echo "⚠️  git pull falló o no hay remoto disponible; continuando con estado local."
fi

# ── 2. PURGE_AND_SYNC ─────────────────────────────────────────────────────────
if [ "${JULES_COMMAND:-}" = "PURGE_AND_SYNC" ]; then
  echo "🧹 Realizando limpieza previa [PURGE_AND_SYNC]..."
  for dir in legacy_old temp_old apps/web-old tests-old legacy integrations/duplicados; do
    if [ -d "$ROOT/$dir" ]; then
      rm -rf "$ROOT/$dir"
      echo "   🗑  Eliminado: $dir"
    fi
  done
fi

# ── 3. Instalar dependencias ──────────────────────────────────────────────────
echo "📦 Instalando dependencias..."
if ! npm install --no-fund --no-audit; then
  echo "❌ npm install falló. Revisa tu package.json y conectividad." >&2
  exit 1
fi

# ── 4. Verificar estructura de directorios críticos ───────────────────────────
echo "📁 Verificando estructura de directorios..."
for dir in docs/patent_EPCT docs/investor_edition src/modules; do
  if [ ! -d "$ROOT/$dir" ]; then
    mkdir -p "$ROOT/$dir"
    touch "$ROOT/$dir/.gitkeep"
    echo "   ✅ Creado: $dir"
  else
    echo "   ✅ Existe: $dir"
  fi
done

# ── 5. Delegar en supercommit_max (sellos + push) ────────────────────────────
exec "$ROOT/supercommit_max.sh" "$@"
