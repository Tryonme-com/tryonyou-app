#!/usr/bin/env bash
# TRYONYOU_SUPERCOMMIT_MAX.sh — Protocolo de Ignición Total TryOnYou (Agente 70)
#
# Pasos de ignición antes del commit/push:
#   1. Verifica que VITE_SHOP_VARIANT esté definido (omitido en --dry-run).
#   2. Limpia la caché de Vite (tryonyou-v100/dist/).
#   3. Delega en supercommit_max.sh con --deploy.
#
# Uso: ./TRYONYOU_SUPERCOMMIT_MAX.sh [opciones supercommit_max] 'Mensaje ...'
# Acepta --dry-run / -n para simular sin ejecutar ni verificar vars.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# ---------------------------------------------------------------------------
# Detectar modo dry-run en los argumentos pasados
# ---------------------------------------------------------------------------
DRY_RUN=0
for _arg in "$@"; do
  [[ "$_arg" == "-n" || "$_arg" == "--dry-run" ]] && DRY_RUN=1 && break
done

# ---------------------------------------------------------------------------
# 1. Verificar VITE_SHOP_VARIANT (solo en modo real)
# ---------------------------------------------------------------------------
if [ "$DRY_RUN" -eq 0 ]; then
  if [ -z "${VITE_SHOP_VARIANT:-}" ]; then
    echo "❌ ERROR: VITE_SHOP_VARIANT no está definido. Define la variable de entorno antes de desplegar." >&2
    exit 1
  fi
  echo "✅ VITE_SHOP_VARIANT verificado."
fi

# ---------------------------------------------------------------------------
# 2. Limpiar caché de Vite (dist/)
# ---------------------------------------------------------------------------
VITE_DIST="${ROOT}/tryonyou-v100/dist"
if [ -d "$VITE_DIST" ]; then
  if [ "$DRY_RUN" -eq 1 ]; then
    echo "🔵 [DRY-RUN] rm -rf $VITE_DIST"
  else
    rm -rf "$VITE_DIST"
    echo "🧹 Caché de Vite limpiada: $VITE_DIST"
  fi
fi

# ---------------------------------------------------------------------------
# 3. Delegar en supercommit_max.sh añadiendo --deploy si no viene ya en args
# ---------------------------------------------------------------------------
_has_deploy=0
for _arg in "$@"; do
  [[ "$_arg" == "-d" || "$_arg" == "--deploy" ]] && _has_deploy=1 && break
done

if [ "$_has_deploy" -eq 1 ]; then
  exec "$ROOT/supercommit_max.sh" "$@"
else
  exec "$ROOT/supercommit_max.sh" --deploy "$@"
fi
