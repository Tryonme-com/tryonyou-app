Memory Notes — bunker_sovereignty.ma
====================================

Objetivo operativo:
- Ejecutar `Supercommit_Max.sh` para sincronizar búnker Oberkampf (75011) con la galería web.
- Reportar cada hito exitoso mediante el notificador `scripts/tryonyou_deploy_bot_notify.py`.

Estado de integración del bot @tryonyou_deploy_bot:
- Token probado: `8788913760:AAE2gS0M8v1_S96H9Fm8I-K1U9Z_6-R-K48`.
- Resultado actual: Telegram responde `401 Unauthorized`.
- Decisión técnica: no detener el pipeline Bash cuando falle la entrega al bot; dejar traza explícita en consola y continuar.

Seguridad (martes 08:00):
- Implementado `dossier_fatality_guard.py`.
- Regla: solo martes >= 08:00.
- Regla: no confirmar ingresos sin evidencia real en `logs/capital_inflows.json` (o ledger custom por `--ledger`).
- Activación: crea `logs/dossier_fatality_state.json` con `fatality_active=true` y evidencia adjunta.

Comandos clave:
- `bash ./Supercommit_Max.sh`
- `python3 dossier_fatality_guard.py --ledger logs/capital_inflows.json --now 2026-04-14T08:00:00`
- `python3 -m unittest -v tests/test_dossier_fatality_guard.py`

Notas de calidad:
- Pipeline validado sin errores de Bash.
- `supercommit_max.sh` ejecutado end-to-end (tests + type-check + build OK).
- El bloqueo pendiente es externo (credencial Telegram inválida/expirada).
