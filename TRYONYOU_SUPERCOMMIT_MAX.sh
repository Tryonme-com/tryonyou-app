#!/bin/bash

# Configuración de Identidad
ORG="Tryonme-com"
REPO="tryonyou-app"
PROJECT_ID="gen-lang-client-0091228222"

echo "========================================"
echo "🚀 INICIANDO SUPERCOMMIT MÁXIMO"
echo "========================================"

# 1. Asegurar que estamos en un repositorio Git
if [ ! -d ".git" ]; then
    git init
    git remote add origin https://github.com/$ORG/$REPO.git
fi

# 2. Sincronizar con la nueva organización
git remote set-url origin https://github.com/$ORG/$REPO.git

# 3. Añadir todos los archivos creados hoy
echo "[+] Indexando módulos del piloto..."
git add tryonyou_demo.py save_silhouette.py smart_cart.py qr_generator.py pilot_manifest.json deploy_pilot.py

# 4. Commit con sello de tiempo y ID de Proyecto
TIMESTAMP=$(date +"%Y-%m-%d %H:%M")
git commit -m "📦 PILOTO V1.1: Demo funcional completa [$PROJECT_ID] - $TIMESTAMP"

# 5. Push a la rama principal
echo "[+] Subiendo a Tryonme-com..."
git branch -M main
git push -u origin main

echo "========================================"
echo "✅ TODO EL TRABAJO ESTÁ A SALVO EN GITHUB"
echo "========================================"
