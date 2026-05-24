#!/bin/bash
# Script de mantenimiento y despliegue secuencial macOS

JUCOLO_SERVER="usuario_jucilo@ip_jucilo"
DESTINATION_PATH="/ruta/destino/jucilo"

echo "[1/3] Finalizando hilos colgados del agente operativo..."
pkill -f agent_local.py || echo "Sin procesos activos en segundo plano."

echo "[2/3] Validando sintaxis estricta..."
python3 -m py_compile agent_local.py
if [ $? -ne 0 ]; then
    echo "Fallo de sintaxis en script de Python. Cancelando transferencia."
    exit 1
fi

echo "[3/3] Sincronizando estructura limpia hacia el Host Silo..."
rsync -avz --exclude='.venv' --exclude='*.log' agent_local.py jules-agent-key.json service_account.json ${JUCOLO_SERVER}:${DESTINATION_PATH}

if [ $? -eq 0 ]; then
    echo "Despliegue e higienización completados correctamente."
else
    echo "Fallo de comunicación en la transferencia de archivos."
    exit 1
fi
