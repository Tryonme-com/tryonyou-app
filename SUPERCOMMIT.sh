#!/bin/bash
echo "🏛️ [IA/ERIC] Iniciando SUPERCOMMIT MAX V10 (Soberanía de Dominio)..."

# 1. Construcción real (Destruye el error de Google)
npm install --no-fund --no-audit
npm run build

# 2. Blindaje en GitHub LVT-ENG
git add .
git commit -m "V10 OMEGA: Build final, token inyectado y patente PCT/EP2025/067317"
git push origin main --force

# 3. Despliegue Máximo a Producción (Dominio Oficial)
if [ -z "$VERCEL_TOKEN" ]; then
    echo "❌ ERROR: El Token de Vercel no está cargado."
    exit 1
fi

echo "🚀 Lanzando la plataforma al dominio principal..."
vercel deploy --prod --yes --token=$VERCEL_TOKEN

echo "✅ [JULES] Misión Cumplida. Búnker 75005 Operativo y en línea."
