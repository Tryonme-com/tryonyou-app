# PROTOCOLO DE AUTONOMÍA TOTAL

## Objetivo
- Target operativo: liquidación de `51,988.50 €` (`#182`) y switch `TEST -> LIVE` (`#187`).

## Regla de ejecución de merge
- Si todas las verificaciones de GitHub están en verde, el agente debe ejecutar el merge automáticamente.
- Si alguna verificación está pendiente o fallida, bloquear merge y abrir diagnóstico inmediato.

## Seguridad y reporte
- Usar exclusivamente el token de Telegram verificado en entorno seguro para reportar el `Fatality` de cada despliegue.
- Nunca exponer tokens, secretos o credenciales en logs, commits o salidas de consola.

## Prioridad técnica inmediata
- Ejecutar limpieza de buffers en AI Studio antes de cada ciclo de despliegue para prevenir el error `motor ocupado`.
- Si reaparece `motor ocupado`, registrar incidente, repetir limpieza y reintentar secuencia de despliegue de forma controlada.

## Estado de decisión
- Gate soberano:
  - `checks == green` -> merge automático.
  - `checks != green` -> no merge + protocolo de corrección.
