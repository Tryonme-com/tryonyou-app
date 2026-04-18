# bunker_sovereignty.ma

MEMORY NOTES — TryOnYou Sovereignty

1) Bot de notificación de despliegue
- Canal: @tryonyou_deploy_bot
- Token operativo (entorno): TELEGRAM_BOT_TOKEN
- Política: reportar éxito de Supercommit_Max y estado de seguridad martes 08:00.

2) Supercommit_Max (sincronización búnker Oberkampf 75011 ↔ galería web)
- Script fuente: supercommit_max.sh
- Modo rápido: --fast (sin build/test)
- Modo deploy: --deploy (usa scripts/deployall.sh)
- Commit con sellos obligatorios:
  @CertezaAbsoluta @lo+erestu PCT/EP2025/067317
  Bajo Protocolo de Soberanía V10 - Founder: Rubén

3) Seguridad martes 08:00
- Script: seguridad_martes_0800.py
- Verifica evidencia vía entorno:
  CAPITAL_450K_STATUS=confirmed
  CAPITAL_450K_AMOUNT_EUR=450000
  CAPITAL_450K_SOURCE=<origen>
- Activa/actualiza dossier_fatality.json en modo protección.

4) Estética/operación
- Sin errores de bash: scripts con shebang + set -euo pipefail.
- Notificaciones Telegram en best-effort (sin bloquear operación principal).
