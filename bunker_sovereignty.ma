MEMORY NOTES — BUNKER SOVEREIGNTY
=================================

Objetivo operacional
- Ejecutar Supercommit_Max en la rama activa, sin force push a main.
- Sincronizar el búnker de Oberkampf (75011) con la galería web.

Canal de notificación
- Bot: @tryonyou_deploy_bot
- Token: usar solo por variable de entorno (nunca hardcodeado).
- Variables esperadas:
  - TRYONYOU_DEPLOY_BOT_TOKEN (fallback: TELEGRAM_BOT_TOKEN / TELEGRAM_TOKEN)
  - TRYONYOU_DEPLOY_BOT_CHAT_ID (fallback: TELEGRAM_CHAT_ID)

Seguridad financiera (martes 08:00)
- Umbral de confirmación: 450.000 EUR.
- Script: martes_0800_fatality_guard.py
- Acción automática al confirmar capital:
  1) Registrar estado en logs/dossier_fatality_state.json
  2) Activar Dossier Fatality (fatality_investors.py)
  3) Notificar por Telegram

Runbook mínimo
1) SUPERCOMMIT_SKIP_BUILD=1 ./supercommit_max.sh
2) CAPITAL_ENTRY_EUR=450000 FATALITY_GUARD_FORCE_WINDOW=1 python3 martes_0800_fatality_guard.py

Sello legal
- @CertezaAbsoluta
- @lo+erestu
- PCT/EP2025/067317
- Bajo Protocolo de Soberanía V10 - Founder: Rubén
