# PROTOCOLO DE AUTONOMIA TOTAL

- **Target:** Liquidacion de 51,988.50 EUR (#182) y Switch TEST->LIVE (#187).
- **Accion:** Si las verificaciones de GitHub estan verdes, el agente debe ejecutar el merge automaticamente cuando exista permiso operativo para hacerlo.
- **Seguridad:** Usar el token de Telegram verificado desde variables de entorno o secretos del pipeline para reportar el "Fatality" de cada despliegue. Nunca hardcodear ni exponer el token en logs, commits o comentarios.
- **Prioridad:** Limpieza de buffers en AI Studio para evitar el error "motor ocupado".

## Guardas Operativas

- No iniciar merge si algun check aparece pendiente, fallido, cancelado, omitido sin justificacion o con estado `UNKNOWN`.
- No activar Switch TEST->LIVE sin confirmacion de entorno, licencia de pago y rutas criticas de verificacion en verde.
- No enviar reportes Telegram si el secreto no esta presente o si el destino no esta verificado.
- Registrar cualquier bloqueo con causa tecnica concreta: checks, permisos, secretos, estado de liquidez o disponibilidad del motor.
