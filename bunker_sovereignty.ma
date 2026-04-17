MEMORY NOTES — BÚNKER SOVEREIGNTY

Archivo solicitado: bunker_sovereignty.ma
Proyecto: TryOnYou / Espejo Digital Soberano
Patente: PCT/EP2025/067317
Protocolo: Bajo Protocolo de Soberanía V10 - Founder: Rubén

Operativa autónoma (resumen):
1) Notificación de éxito:
   - Bot obligatorio: @tryonyou_deploy_bot
   - Token por entorno: TRYONYOU_DEPLOY_BOT_TOKEN (fallback TELEGRAM_BOT_TOKEN/TELEGRAM_TOKEN)
   - Chat por entorno: TRYONYOU_DEPLOY_CHAT_ID (fallback TELEGRAM_CHAT_ID)

2) Despliegue:
   - Ejecutar Supercommit_Max para sincronizar búnker Oberkampf (75011) y galería web.
   - Script recomendado: supercommit_max.sh
   - Validar sintaxis Bash antes del despliegue.

3) Seguridad (martes 08:00 Europe/Paris):
   - Confirmar entrada de 450000 EUR.
   - Fuente preferida: SOVEREIGN_CONFIRMED_CAPITAL_EUR.
   - Fallback: suma de CONFIRMADO en registro_pagos_hoy.csv.
   - Si >= 450000 EUR: activar Dossier Fatality y registrar evidencia.
   - Forzado manual: SOVEREIGN_FORCE_SECURITY_CHECK=1.

4) Estética / calidad:
   - Objetivo "10/10 sin errores de Bash".
   - Comprobación mínima: bash -n en scripts críticos de commit/despliegue.
