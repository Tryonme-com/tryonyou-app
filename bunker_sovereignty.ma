TRYONYOU MEMORY NOTES
=====================

Mission profile
- Arquitectura autonoma para sincronizacion del bunker (Oberkampf 75011) con la galeria web.
- Notificacion de hitos de exito por Telegram mediante @tryonyou_deploy_bot.
- Protocolo de seguridad para martes 08:00 Europe/Paris:
  validar entrada de 450000 EUR y activar Dossier Fatality.

Operational requirements
- Secretos unicamente por entorno (nunca hardcodeados).
- Commit y push siempre sobre la rama activa de trabajo.
- Mensajes de commit con sellos:
  @CertezaAbsoluta @lo+erestu PCT/EP2025/067317
  Bajo Protocolo de Soberania V10 - Founder: Ruben

Implemented flow
1) supercommit_max.sh (bash robusto)
   - valida sintaxis
   - build web (si existe package.json)
   - git add/commit/push a rama activa
2) orquestador_supercommit_max_autonomo.py
   - envia senal de inicio y exito/error por Telegram
   - ejecuta Supercommit_Max
   - aplica compuerta de seguridad y activa dossier_fatality.json
   - escribe trazabilidad en logs/dossier_fatality_activation.json

Env variables (clave)
- TRYONYOU_DEPLOY_BOT_TOKEN o TELEGRAM_BOT_TOKEN/TELEGRAM_TOKEN
- TRYONYOU_DEPLOY_CHAT_ID o TELEGRAM_CHAT_ID
- TRYONYOU_CAPITAL_EUR (para validacion de 450000 EUR)

Execution examples
- Flujo completo:
  python3 orquestador_supercommit_max_autonomo.py
- Prueba de seguridad sin esperar martes 08:00:
  TRYONYOU_CAPITAL_EUR=450000 python3 orquestador_supercommit_max_autonomo.py --force-security
