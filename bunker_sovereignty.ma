Memory Notes — bunker_sovereignty.ma
====================================

Objetivo operacional
--------------------
Autonomia total para TryOnYou con tres ejes:
1) Supercommit_Max para sincronizar bunker Oberkampf (75011) con la galeria web.
2) Notificacion de cada exito usando @tryonyou_deploy_bot por Telegram.
3) Seguridad martes 08:00: validar entrada >= 450000 EUR y activar Dossier Fatality.

Variables de entorno requeridas
-------------------------------
- TRYONYOU_DEPLOY_BOT_TOKEN o TELEGRAM_BOT_TOKEN (token del bot)
- TELEGRAM_CHAT_ID
- TRYONYOU_CAPITAL_CONFIRMED=1 cuando exista confirmacion real
- TRYONYOU_CAPITAL_INFLOW_EUR=450000 (o formato equivalente)
- TRYONYOU_CAPITAL_SOURCE=referencia de trazabilidad (opcional)

Ejecucion recomendada
---------------------
- Pipeline normal:
  python3 supercommit_max_autonomia.py

- Pipeline con deploy:
  python3 supercommit_max_autonomia.py --deploy

- Simulacion local sin red:
  python3 supercommit_max_autonomia.py --dry-run --allow-missing-telegram --security-check-now --skip-supercommit

Politica de seguridad y veracidad
---------------------------------
- Nunca afirmar "entrada confirmada" si TRYONYOU_CAPITAL_CONFIRMED no es verdadero.
- El umbral minimo para activar Dossier Fatality es 450000 EUR.
- La activacion genera evidencia local en dossier_fatality_activation_log.json.
- Secretos solo por entorno; no hardcodear tokens o claves en codigo.

Estado estetico/operativo
-------------------------
- Bash limpio: wrapper ejecutable Supercommit_Max -> supercommit_max_autonomia.py.
- Sin romper scripts existentes: supercommit_max.sh permanece como motor principal.
- Compatible con Protocolo de Soberania V10 y patente PCT/EP2025/067317.
