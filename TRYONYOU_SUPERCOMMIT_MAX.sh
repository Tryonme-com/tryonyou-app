#!/usr/bin/env bash
# TRYONYOU_SUPERCOMMIT_MAX — Agente 70: Ignición Total.
#
# Flujo:
#   1. Verifica que VITE_SHOP_VARIANT esté definida.
#   2. Limpia la caché de Vite (node_modules/.vite y dist/).
#   3. Delega el commit (con sellos obligatorios) en supercommit_max.sh.
#   4. Si se pasa --deploy (o -d), esa opción se reenvía a supercommit_max.sh;
#      este script no añade --force automáticamente.
#
# Opciones propias:
#   --skip-env-check   Omite la verificación de VITE_SHOP_VARIANT (útil en CI que inyecta la var tarde).
#   --skip-cache-clean Omite la limpieza de la caché de Vite.
#   Todas las demás opciones se reenvían a supercommit_max.sh.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

SKIP_ENV_CHECK=0
SKIP_CACHE_CLEAN=0
PASSTHROUGH_ARGS=()

while [[ $# -gt 0 ]]; do
  case "$1" in
    --skip-env-check)   SKIP_ENV_CHECK=1;   shift ;;
    --skip-cache-clean) SKIP_CACHE_CLEAN=1; shift ;;
    *) PASSTHROUGH_ARGS+=("$1"); shift ;;
  esac
done

# ---------------------------------------------------------------------------
# 1. Verificación de VITE_SHOP_VARIANT
# ---------------------------------------------------------------------------
if [ "$SKIP_ENV_CHECK" -eq 0 ]; then
  if [ -z "${VITE_SHOP_VARIANT:-}" ]; then
    echo "❌ ERROR: VITE_SHOP_VARIANT no está definida. Define la variable de entorno antes de ejecutar este script." >&2
    exit 1
  fi
  echo "✅ VITE_SHOP_VARIANT detectada: ${VITE_SHOP_VARIANT}"
fi

# ---------------------------------------------------------------------------
# 2. Limpieza de la caché de Vite
# ---------------------------------------------------------------------------
if [ "$SKIP_CACHE_CLEAN" -eq 0 ]; then
  echo "🧹 Limpiando caché de Vite..."
  rm -rf "$ROOT/node_modules/.vite" "$ROOT/dist"
  echo "✅ Caché de Vite eliminada."
fi

# ---------------------------------------------------------------------------
# 3. Delegar en supercommit_max (add + commit con sellos + push + deploy opcional)
# ---------------------------------------------------------------------------
exec "$ROOT/supercommit_max.sh" "${PASSTHROUGH_ARGS[@]+"${PASSTHROUGH_ARGS[@]}"}"
