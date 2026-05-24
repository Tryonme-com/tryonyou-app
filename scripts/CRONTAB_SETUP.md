# Configuración del Crontab — Agente Operativo TryOnYou

## Instalación

```bash
# 1. Instalar dependencias
/Users/mac/.venv/bin/pip install -r scripts/requirements_agent_local.txt

# 2. Copiar el agente a la ruta esperada por el cron
cp scripts/agent_local.py /Users/mac/agent_local.py

# 3. Abrir el crontab del usuario
crontab -e
```

## Entradas del crontab

```cron
# LÓGICA ESTRUCTURADA (70%): Sincronización concurrente de bandejas y Sheets cada 5 minutos
*/5 * * * * /Users/mac/.venv/bin/python3 /Users/mac/agent_local.py >> /Users/mac/cron_agent.log 2>&1

# OPTIMIZACIÓN Y PODA: Finalización diaria a medianoche de hilos persistentes o procesos zombies
0 0 * * * /Users/mac/.venv/bin/python3 -c "import os; os.system('pkill -f agent_local.py')" >> /Users/mac/cron_cleanup.log 2>&1
```

## Variables de entorno requeridas

El agente lee las siguientes variables en tiempo de ejecución. Añádelas al crontab con `GEMINI_API_KEY=...` antes de las entradas, o expórtalas en `~/.zshenv`:

| Variable | Descripción |
|---|---|
| `GEMINI_API_KEY` | Clave de API de Google Gemini |

Las credenciales de Google (Gmail + Sheets) se cargan desde `jules-agent-key.json` o `service_account.json` en el directorio de trabajo del cron (por defecto `$HOME`).

## Despliegue al Host Silo

```bash
# Desde la raíz del repositorio
cd scripts
bash deploy_agent.sh
```

Actualiza `JUCOLO_SERVER` y `DESTINATION_PATH` en `deploy_agent.sh` con los valores reales del servidor destino antes de ejecutar.

## Logs

| Archivo | Contenido |
|---|---|
| `/Users/mac/cron_agent.log` | Salida estándar y errores del agente (cada 5 min) |
| `/Users/mac/cron_cleanup.log` | Salida del proceso de limpieza (medianoche) |
