#!/usr/bin/env bash
# percommit_max.sh — Filtro de Vulgarización TryOnYou
#
# Antes de delegar en supercommit_max.sh, analiza el diff staged y bloquea:
#   - Etiquetas de talla de ropa: S, M, L como palabras independientes.
#   - Exposición del Admin Token de Shopify (shpat_* o SHOPIFY_ADMIN_ACCESS_TOKEN=<valor>).
#
# En modo --dry-run / -n los filtros se omiten (sin diff real que analizar).
# Uso: ./percommit_max.sh [opciones supercommit_max] 'Mensaje ...'
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# ---------------------------------------------------------------------------
# Detectar modo dry-run
# ---------------------------------------------------------------------------
DRY_RUN=0
for _arg in "$@"; do
  [[ "$_arg" == "-n" || "$_arg" == "--dry-run" ]] && DRY_RUN=1 && break
done

# ---------------------------------------------------------------------------
# Filtros de contenido (solo en modo real)
# ---------------------------------------------------------------------------
if [ "$DRY_RUN" -eq 0 ]; then
  STAGED_DIFF="$(git diff --cached 2>/dev/null || true)"

  # Bloquear etiquetas de talla S, M, L en líneas añadidas del diff
  if echo "$STAGED_DIFF" | grep -qE '^\+.*\b[SML]\b'; then
    echo "❌ BLOQUEADO: El diff contiene etiquetas de talla (S, M, L). Usa medidas numéricas en cm." >&2
    exit 1
  fi

  # Bloquear exposición del Admin Token de Shopify
  if echo "$STAGED_DIFF" | grep -qE '^\+.*(shpat_[A-Za-z0-9_]+|SHOPIFY_ADMIN_ACCESS_TOKEN=[^[:space:]]{3,})'; then
    echo "❌ BLOQUEADO: El diff contiene el Admin Token de Shopify. Nunca comitas tokens de acceso." >&2
    exit 1
  fi
fi

exec "$ROOT/supercommit_max.sh" "$@"
