MEMORY NOTES - TRYONYOU BUNKER SOVEREIGNTY
==========================================

1) BOT DE NOTIFICACION
- Bot operativo requerido: @tryonyou_deploy_bot
- Nunca hardcodear token en codigo fuente.
- Variables recomendadas:
  - TRYONYOU_DEPLOY_BOT_TOKEN
  - TRYONYOU_DEPLOY_CHAT_ID
  - fallback: TELEGRAM_BOT_TOKEN / TELEGRAM_TOKEN + TELEGRAM_CHAT_ID

2) SUPERCOMMIT_MAX
- Script soberano: supercommit_max.sh
- Flujo:
  a) git add -A
  b) commit con sellos obligatorios
  c) push a rama actual (sin forzar)
  d) notificacion de exito por Telegram
- Sellos obligatorios:
  - @CertezaAbsoluta
  - @lo+erestu
  - PCT/EP2025/067317
  - Bajo Protocolo de Soberania V10 - Founder: Ruben

3) SEGURIDAD MARTES 08:00
- Script: seguridad_450k_martes_0800.py
- Regla:
  - Solo dispara martes 08:00 hora local (Europe/Paris por defecto).
  - Verifica total CONFIRMADO >= 450000 EUR en ledger CSV.
  - Si cumple, activa Dossier Fatality en dossier_fatality.json.
  - Si no cumple, no activa nada.

4) ESTETICA / BASH
- Todo script bash debe pasar validacion sintactica con:
  bash -n <script>
- En caso de fallo, corregir antes de ejecutar push.
