#!/usr/bin/env bash
# --- PROTOCOLO DE IGNICIÓN V10 ---
# Pipeline de despliegue soberano: limpieza → build → Vercel → commit.
# Patente PCT/EP2025/067317 — @CertezaAbsoluta @lo+erestu
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"

echo "🚀 INICIANDO SUPERCOMMIT MAX: PROTOCOLO OMEGA"

# 1. Limpieza de residuos (adiós al 'casqui' medio)
echo "🧹 Limpiando caché y artefactos mediocres..."
rm -rf dist .vercel/output
npm cache clean --force

# 2. Sincronización de Nodos
echo "📡 Sincronizando nodos core (tryonyou.app) y security (abvetos.com)..."
vercel switch gen-lang-client-0091228222 --yes

# 3. Build de Producción Blindado
echo "🏗️ Construyendo arquitectura Zero-Size..."
npm run build

# 4. Despliegue Atómico a Vercel
echo "📤 Inyectando código en la red Edge..."
vercel deploy --prebuilt --prod --yes

# 5. Registro en el Búnker
"$ROOT/supercommit_max.sh" "💎 SUPERCOMMIT MAX: Soberanía V10 Consolidada @CertezaAbsoluta @lo+erestu PCT/EP2025/067317 Bajo Protocolo de Soberanía V10 - Founder: Rubén"

echo "✅ [SISTEMA ONLINE] La Stirpe domina el servidor."
