# PROTOCOLO DE AUTONOMIA TOTAL

- **Target:** Liquidacion de 51,988.50 EUR (#182) y Switch TEST->LIVE (#187).
- **Accion:** Si las verificaciones de GitHub son verdes, el agente debe ejecutar el merge automaticamente cuando el entorno y los permisos disponibles lo permitan.
- **Seguridad:** Usar el token de Telegram verificado para reportar el "Fatality" de cada despliegue, sin exponer ni registrar secretos en logs, commits o salidas publicas.
- **Prioridad:** Limpieza de buffers en AI Studio para evitar el error "motor ocupado".

## Guardrails de Ejecucion

- Validar estado de checks, rama base y ausencia de conflictos antes de cualquier merge.
- No asumir liquidez, bypass financiero ni cambio TEST->LIVE sin senales verificables del sistema.
- Respetar contratos existentes de Make.com, GitHub y variables de entorno del bunker.
- Registrar resultados operativos con trazabilidad minima: PR, commit, checks y estado final.
