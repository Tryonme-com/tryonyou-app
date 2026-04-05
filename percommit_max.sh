#!/usr/bin/env bash
# percommit_max — Filtro de Vulgarización: bloquea commits con etiquetas de talla
# ( S / M / L ) o con tokens de administración de Shopify expuestos, luego delega
# el commit en supercommit_max.sh.
#
# Uso: ./percommit_max.sh [opciones de supercommit_max] 'Mensaje @CertezaAbsoluta @lo+erestu PCT/EP2025/067317'
#
# Opciones propias (consumidas antes de pasar el resto a supercommit_max):
#   --skip-security-check   Omite el análisis de contenido (útil en dry-run de CI).
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

SKIP_SECURITY_CHECK=0
PASSTHROUGH_ARGS=()

while [[ $# -gt 0 ]]; do
  case "$1" in
    --skip-security-check) SKIP_SECURITY_CHECK=1; shift ;;
    *) PASSTHROUGH_ARGS+=("$1"); shift ;;
  esac
done

# ---------------------------------------------------------------------------
# Filtro de seguridad: inspecciona el diff staged y el mensaje de commit
# ---------------------------------------------------------------------------
if [ "$SKIP_SECURITY_CHECK" -eq 0 ]; then
  # 1. Detecta etiquetas de talla sueltas ("S", "M" o "L" como palabra completa)
  # en el diff staged (para evitar exponer variantes de talla en texto plano).
  STAGED_DIFF="$(git diff --cached 2>/dev/null || true)"
  if echo "$STAGED_DIFF" | grep -qE '(^|[^A-Za-z])(S|M|L)([^A-Za-z]|$)'; then
    echo "❌ BLOQUEADO: el diff staged contiene etiquetas de talla (S, M, L) en texto plano. Usa constantes o enumeraciones en su lugar." >&2
    exit 1
  fi

  # 2. Detecta patrones de Shopify Admin Token (shpat_ o shpca_ como prefijo).
  if echo "$STAGED_DIFF" | grep -qE 'shp(at|ca)_[A-Za-z0-9_-]{10,}'; then
    echo "❌ BLOQUEADO: se ha detectado un posible Shopify Admin Token en el diff staged. Retira el secreto del código antes de continuar." >&2
    exit 1
  fi

  echo "✅ Filtro de seguridad superado: sin etiquetas de talla ni tokens de Shopify expuestos."
fi

# ---------------------------------------------------------------------------
# Delegar en supercommit_max
# ---------------------------------------------------------------------------
exec "$ROOT/supercommit_max.sh" "${PASSTHROUGH_ARGS[@]+"${PASSTHROUGH_ARGS[@]}"}"
