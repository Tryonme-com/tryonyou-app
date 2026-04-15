MEMORY NOTES — bunker_sovereignty.ma

1) Notificación de éxito (obligatoria)
- Bot objetivo: @tryonyou_deploy_bot
- Token operativo:
  usar el token seguro recibido por canal operativo (no versionar en git)
- Canal de uso en scripts:
  - TRYONYOU_DEPLOY_BOT_TOKEN (preferente)
  - fallback: TELEGRAM_BOT_TOKEN / TELEGRAM_TOKEN
  - chat_id: TRYONYOU_DEPLOY_CHAT_ID o TELEGRAM_CHAT_ID

2) Despliegue / sincronización
- Comando maestro:
  ./supercommit_max.sh -m "chore: Supercommit Max bunker-web sync"
- Objetivo:
  Sincronizar búnker Oberkampf (75011) con galería web.
- Resultado esperado:
  build OK + git push en rama activa + notificación Telegram de éxito.

3) Seguridad (martes 08:00)
- Script:
  python3 seguridad_martes_0800.py
- Forzado manual:
  python3 seguridad_martes_0800.py --run-now
- Regla:
  Confirmar 450000 EUR (CSV de pagos confirmados) y activar Dossier Fatality.
- Evidencia:
  dossier_fatality_activation.json

4) Cron recomendado (producción)
- 0 8 * * 2 cd /workspace && /usr/bin/env FATALITY_SEND_TELEGRAM=1 TRYONYOU_DEPLOY_BOT_TOKEN='***' TRYONYOU_DEPLOY_CHAT_ID='***' python3 seguridad_martes_0800.py

5) Estética/operación
- Mantener ejecución sin errores de Bash (set -euo pipefail).
- No exponer secretos en logs, commits ni JSON versionados.
