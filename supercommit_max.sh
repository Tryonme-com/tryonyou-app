#!/bin/bash

# ==============================================================================
# Nombre: supercommit_max.sh
# Descripción: Automatización de Git con validación de integridad.
# ==============================================================================

# Colores para salida técnica
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}[START] Iniciando proceso de commit...${NC}"

# 1. Comprobar si es un repositorio Git
if [ ! -d .git ]; then
    echo -e "${RED}[ERROR] No se detectó un repositorio Git en este directorio.${NC}"
    exit 1
fi

# 2. Añadir todos los cambios
git add .

# 3. Validar si hay cambios para procesar
if git diff --cached --quiet; then
    echo -e "${RED}[SKIP] No hay cambios para confirmar.${NC}"
    exit 0
fi

# 4. Definir mensaje de commit (Argumento o Default)
MESSAGE=${1:-"Update: $(date +'%Y-%m-%d %H:%M:%S')"}

# 5. Ejecutar Commit
if git commit -m "$MESSAGE"; then
    echo -e "${GREEN}[OK] Commit realizado: $MESSAGE${NC}"
else
    echo -e "${RED}[ERROR] Falló el commit.${NC}"
    exit 1
fi

# 6. Push a la rama actual
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)

if git push origin "$CURRENT_BRANCH"; then
    echo -e "${GREEN}[SUCCESS] Cambios subidos a 'origin/$CURRENT_BRANCH'.${NC}"
else
    echo -e "${RED}[ERROR] Falló el push. Verifique conexión o conflictos.${NC}"
    exit 1
fi

echo -e "${GREEN}[FINISH] Operación completada con éxito.${NC}"
