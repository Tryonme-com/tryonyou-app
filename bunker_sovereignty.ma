# Memory Notes — bunker_sovereignty.ma
# TryOnYou / Espejo Digital Soberano

memory_notes:
  bot:
    username: "@tryonyou_deploy_bot"
    token_source:
      - TRYONYOU_DEPLOY_BOT_TOKEN
      - TELEGRAM_BOT_TOKEN
      - TELEGRAM_TOKEN
    chat_source:
      - TRYONYOU_DEPLOY_CHAT_ID
      - TELEGRAM_CHAT_ID

  deploy:
    command: "python3 orquestador_autonomia_total.py --supercommit-fast --force-time-window --expected-capital 450000"
    objective: "Sincronizar bunker Oberkampf (75011) con galeria web sin errores de Bash."

  security:
    checkpoint:
      weekday: "Tuesday"
      time: "08:00"
      timezone: "Europe/Paris"
      expected_capital_eur: 450000
    fatality:
      protocol: "Dossier Fatality"
      output_dir: "dossiers/fatality/"
      vip_flow_alert_threshold_pct: 99

  legal:
    patent: "PCT/EP2025/067317"
    siret: "94361019600017"
    founder: "Ruben Espinar Rodriguez"

  notes:
    - "Nunca hardcodear tokens o secretos en codigo."
    - "Reportar cada exito operativo por Telegram."
    - "Si VIP_FLOW_RATE < 99, marcar alerta en dossier."
