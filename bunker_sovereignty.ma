Memory Notes - TryOnYou Sovereignty
===================================

1) Supercommit_Max
- Script principal: ./supercommit_max.sh
- Objetivo: sincronizar bunker Oberkampf (75011) con galeria web.
- Flujo: check seguridad Fatality -> build web -> commit con sellos -> push.

2) Notificacion de exito
- Bot requerido: @tryonyou_deploy_bot
- Configurar por entorno (nunca en codigo):
  - TRYONYOU_DEPLOY_BOT_TOKEN
  - TRYONYOU_DEPLOY_BOT_CHAT_ID
- Fallbacks compatibles:
  - TELEGRAM_BOT_TOKEN / TELEGRAM_TOKEN
  - TELEGRAM_CHAT_ID

3) Seguridad (martes 08:00)
- Script: ./security_tuesday_fatality.py
- Ventana de control: martes, hora 08 local.
- Umbral por defecto: 450000 EUR (FATALITY_EXPECTED_AMOUNT_EUR).
- Evidencia de activacion: logs/dossier_fatality_activation.json

4) Sellos obligatorios de commit
- @CertezaAbsoluta
- @lo+erestu
- PCT/EP2025/067317
- Bajo Protocolo de Soberania V10 - Founder: Ruben

