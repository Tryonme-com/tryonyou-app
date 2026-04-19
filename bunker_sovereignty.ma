TRYONYOU MEMORY NOTES — BUNKER SOVEREIGNTY
=========================================

Archivo de referencia para automatizaciones soberanas del búnker.

1) Supercommit_Max
- Comando estándar:
  bash supercommit_max.sh --fast --msg "Sincronización Oberkampf 75011 con galería web"
- Sellos obligatorios se anexan automáticamente:
  @CertezaAbsoluta @lo+erestu PCT/EP2025/067317
  Bajo Protocolo de Soberanía V10 - Founder: Rubén

2) Notificación de éxito por bot
- Variables requeridas (nunca hardcodear secretos):
  TRYONYOU_DEPLOY_BOT_TOKEN
  TRYONYOU_DEPLOY_CHAT_ID
- Fallbacks soportados:
  TELEGRAM_BOT_TOKEN / TELEGRAM_TOKEN y TELEGRAM_CHAT_ID

3) Seguridad martes 08:00 (Paris)
- Script: python3 martes_0800_fatality_guard.py
- Ventana por defecto: martes 08:00-08:09 Europe/Paris
- Confirmación de capital esperada: 450000 EUR (lee .emergency_payout)
- Activa estado "dossier_fatality" y escribe:
  logs/dossier_fatality_tuesday_0800.json

4) Entorno de confirmación de capital
- SECURITY_CONFIRMED_CAPITAL_EUR (preferido)
- CONFIRMED_CAPITAL_EUR
- QONTO_BALANCE_EUR

