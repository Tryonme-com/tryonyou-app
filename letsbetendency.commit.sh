#!/usr/bin/env bash
# =================================================================
# TRYONYOU V14 ARMORED - PROTOCOLO DE CONSOLIDACIÓN SOBERANA
# OBJETIVO: Resolver FUNCTION_INVOCATION_FAILED y liberar Hito 2
# =================================================================

set -Eeuo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT_DIR"

echo "🔱 Iniciando Operación Soberanía Total..."

# 1. LIMPIEZA DE INFRAESTRUCTURA
echo "🛠️ Limpiando caché y módulos corruptos..."
rm -rf node_modules .next dist

if command -v pnpm >/dev/null 2>&1; then
  pnpm install --frozen-lockfile || pnpm install
else
  echo "⚠️ pnpm no está instalado; usando npm install como fallback."
  npm install
fi

# 2. VALIDACIÓN DE ENTORNO (SINCERIDAD RADICAL)
echo "🔑 Verificando variables de Stripe y Supabase..."
if command -v vercel >/dev/null 2>&1; then
  vercel env pull .env.production --yes || {
    echo "⚠️ No se pudo ejecutar 'vercel env pull'. Revisa autenticación/token."
  }
else
  echo "⚠️ Vercel CLI no está instalado; omitiendo env pull automático."
fi

if [[ -f .env.production ]]; then
  REQUIRED_VARS=(
    STRIPE_SECRET_KEY
    STRIPE_WEBHOOK_SECRET
    SUPABASE_URL
    SUPABASE_ANON_KEY
    SUPABASE_SERVICE_ROLE_KEY
  )

  has_missing_vars=0
  for var in "${REQUIRED_VARS[@]}"; do
    if ! grep -Eq "^${var}=" .env.production; then
      echo "❌ Falta variable: ${var}"
      has_missing_vars=1
    fi
  done

  if [[ "$has_missing_vars" -eq 0 ]]; then
    echo "✅ Variables críticas detectadas."
  fi
else
  echo "⚠️ .env.production no existe; no se pudo validar variables."
fi

# 3. REPARACIÓN DEL RUNTIME PYTHON
echo "🐍 Ajustando runtime de Jules V7 Agent..."
cat > runtime.txt <<'EOF'
python-3.12.3
EOF
echo "✅ runtime.txt actualizado con python-3.12.3."

echo "🏁 Operación completada."
