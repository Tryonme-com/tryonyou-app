TRYONYOU // BUNKER SOVEREIGNTY NOTES
Patente: PCT/EP2025/067317
Protocolo: Bajo Protocolo de Soberanía V10 - Founder: Rubén

Objetivo:
- Orquestar Supercommit_Max con autonomia total y sin hardcodear secretos.
- Sincronizar bunker Oberkampf 75011 con la galeria web.
- Notificar exitos por Telegram via bot de despliegue configurado en entorno.
- Activar Dossier Fatality solo con confirmacion verificable de 450000 EUR.

Checklist operativo:
- TRYONYOU_DEPLOY_BOT_TOKEN (o TELEGRAM_BOT_TOKEN/TELEGRAM_TOKEN) en entorno.
- TRYONYOU_DEPLOY_BOT_CHAT_ID (o TELEGRAM_CHAT_ID) en entorno.
- TRYONYOU_CAPITAL_CONFIRMED=true y TRYONYOU_CAPITAL_INFLOW_EUR>=450000.
- TRYONYOU_CAPITAL_EVIDENCE_FILE apuntando a evidencia real verificable.

Regla de seguridad:
- Nunca afirmar confirmaciones bancarias sin evidencia.
