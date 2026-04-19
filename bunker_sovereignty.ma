BUNKER_SOVEREIGNTY_MEMORY_NOTES
================================

Objetivo:
- Autonomia total del piloto financiero de TryOnYou para PRs de Bancaria/Settlement.

Archivo operativo principal:
- BUNKER_AUTO_PILOT.py

Variables de entorno requeridas:
- GITHUB_TOKEN
- BUNKER_GITHUB_REPO (default: tryonme-com/tryonyou-app)
- TELEGRAM_BOT_TOKEN (o TELEGRAM_TOKEN o TRYONYOU_DEPLOY_BOT_TOKEN)
- TELEGRAM_CHAT_ID (default y bot objetivo: @tryonyou_deploy_bot)
- RENDER_HEALTHCHECK_URL
- STRIPE_WEBHOOK_HEALTH_URL (opcional; sin esta URL usa tests locales de Stripe)
- BUNKER_SUPERCOMMIT_FAST (default: false; se recomienda FULL para sincronizar bunker + galeria)
- BUNKER_SUPERCOMMIT_MESSAGE

Directriz de notificacion:
- Reportar cada exito del flujo via @tryonyou_deploy_bot.
- Nunca hardcodear token en codigo, commits o logs.

Seguridad martes 08:00 (Europe/Paris):
- BUNKER_CAPITAL_ENTRY_EUR (default: 450000.0)
- BUNKER_CAPITAL_ENTRY_CONFIRMED=true  (obligatorio para activar Dossier Fatality)
- BUNKER_TIMEZONE (default: Europe/Paris)
- Requiere importe objetivo exacto de 450000.00 EUR para activar Dossier Fatality.

Impacto financiero reportado:
- BUNKER_FINANCIAL_IMPACT_EUR (default: 51988.50)

Ejecucion:
- python3 BUNKER_AUTO_PILOT.py

Resultados esperados:
1) Detecta PRs objetivo (#182, #187, Bancaria, Settlement).
2) Valida Render + Stripe + Supercommit_Max + sintaxis Bash (global de scripts .sh).
3) Hace merge automatico si todo esta OK.
4) Envia exito a Telegram por cada hito en verde y merge final.
5) En martes 08:00 activa dossier_fatality_activation.json si capital confirmado.

Nota operativa de interfaz:
- Si un flujo pide elegir "Memory Notes", usar este archivo:
  bunker_sovereignty.ma
