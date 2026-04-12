TRYONYOU MEMORY NOTES — BUNKER SOVEREIGNTY
==========================================

Operational checkpoints
- Use `supercommit_max.sh` as canonical CI/CD gate (vault check, tests, typecheck, build, git).
- Keep commit stamps mandatory:
  @CertezaAbsoluta @lo+erestu PCT/EP2025/067317
  Bajo Protocolo de Soberanía V10 - Founder: Rubén

Security protocol (Tuesday 08:00 Europe/Paris)
- Script: `python3 martes_0800_dossier_fatality.py`
- Required capital confirmation: 450000 EUR.
- Environment input accepted:
  TRYONYOU_CONFIRMED_CAPITAL_EUR (preferred)
- Optional force execution:
  python3 martes_0800_dossier_fatality.py --force --confirmed-eur 450000

Telegram success reporting
- Bot handle reference: @tryonyou_deploy_bot
- Configure via environment (never hardcode secrets):
  TRYONYOU_DEPLOY_BOT_TOKEN
  TRYONYOU_DEPLOY_CHAT_ID

Sovereign fit and visual quality
- Keep gallery quality 10/10 with zero Bash syntax errors.
- Validate with:
  bash -n supercommit_max.sh
  npm run build
