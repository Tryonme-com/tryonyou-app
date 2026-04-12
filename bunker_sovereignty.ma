BUNKER_SOVEREIGNTY_MEMORY_NOTES
================================

Objetivo:
- Autonomia total del piloto financiero de TryOnYou para PRs de Bancaria/Settlement.

Archivo operativo principal:
- BUNKER_AUTO_PILOT.py

Variables de entorno requeridas:
- GITHUB_TOKEN
- BUNKER_GITHUB_REPO (default: tryonme-com/tryonyou-app)
- TELEGRAM_BOT_TOKEN (o TELEGRAM_TOKEN)
- TELEGRAM_CHAT_ID (default: @tryonyou_deploy_bot)
- RENDER_HEALTHCHECK_URL
- STRIPE_WEBHOOK_HEALTH_URL (opcional; sin esta URL usa tests locales de Stripe)

Seguridad martes 08:00 (Europe/Paris):
- BUNKER_CAPITAL_ENTRY_EUR (default: 450000.0)
- BUNKER_CAPITAL_ENTRY_CONFIRMED=true  (obligatorio para activar Dossier Fatality)
- BUNKER_TIMEZONE (default: Europe/Paris)

Impacto financiero reportado:
- BUNKER_FINANCIAL_IMPACT_EUR (default: 51988.50)

Ejecucion:
- python3 BUNKER_AUTO_PILOT.py

Resultados esperados:
1) Detecta PRs objetivo (#182, #187, Bancaria, Settlement).
2) Valida Render + Stripe + Supercommit_Max + sintaxis Bash.
3) Hace merge automatico si todo esta OK.
4) Envia exito a Telegram.
5) En martes 08:00 activa dossier_fatality_activation.json si capital confirmado.
