#!/bin/bash

# ==============================================================================
# PROTOCOLO ULTIMATUM V10 - CORE DE ORQUESTACIÓN SOBERANA
# ==============================================================================

# Definición de estilos y colores para logs técnicos
ROJO='\033[0;31m'    
VERDE='\033[0;32m'   
AMARILLO='\033[0;33m'
AZUL='\033[0;34m'  
SIN_COLOR='\033[0m'

echo -e "${AZUL}=== [INICIANDO PROTOCOLO ULTIMATUM V10] ===${SIN_COLOR}"

# Verificación de git local
if [ -d ".git" ]; then
    echo -e "${VERDE}[+] Repositorio Git detectado.${SIN_COLOR}"
    git add .
    git commit -m "Auto-commit: Optimización e inyección de arquitectura unificada"
    echo -e "${VERDE}[SUCCESS] Cambios consolidados localmente.${SIN_COLOR}"
else
    echo -e "${AMARILLO}[!] Advertencia: No se detectó un entorno Git en este directorio.${SIN_COLOR}"
fi

echo -e "${AZUL}=== [PROTOCOLO COMPLETADO] ===${SIN_COLOR}"
