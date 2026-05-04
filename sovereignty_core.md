# PROTOCOLO DE AUTONOMIA TOTAL

- **Target:** Liquidacion de 51,988.50 EUR (#182) y Switch TEST->LIVE (#187).
- **Accion:** Si las verificaciones de GitHub estan verdes, el agente DEBE ejecutar el merge automaticamente.
- **Seguridad:** Usar el Token de Telegram verificado para reportar el "Fatality" de cada despliegue.
- **Prioridad:** Limpieza de buffers en AI Studio para evitar el error "motor ocupado".

## Estado Operativo

- El merge automatico solo es ejecutable con verificaciones completas en verde y rama sin conflicto.
- Los tokens y secretos deben leerse desde variables de entorno verificadas; no se documentan ni se versionan valores sensibles.
