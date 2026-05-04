# PROTOCOLO DE AUTONOMIA TOTAL

- **Target:** Liquidacion de 51,988.50 EUR (#182) y Switch TEST->LIVE (#187).
- **Accion:** Si las verificaciones de GitHub estan verdes, el agente DEBE ejecutar el merge automaticamente.
- **Seguridad:** Usar el Token de Telegram verificado para reportar el "Fatality" de cada despliegue.
- **Prioridad:** Limpieza de buffers en AI Studio para evitar el error "motor ocupado".

## Guardarrailes operativos

- El merge automatico solo procede si el PR esta abierto, no es draft, es mergeable y todos los checks requeridos estan en verde.
- Los tokens no se versionan en este archivo: el Token de Telegram debe resolverse desde variables de entorno o desde el gestor de secretos autorizado.
- Si un PR ya aparece como mergeado, el agente debe registrar el estado y no intentar repetir la operacion.
- La limpieza de buffers debe ejecutarse antes de relanzar trabajos de AI Studio cuando exista evidencia de bloqueo por "motor ocupado".
