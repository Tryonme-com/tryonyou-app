# PROTOCOLO DE AUTONOMIA TOTAL

## Objetivo

- **Target financiero:** liquidacion de **51,988.50 EUR** vinculada a `#182`.
- **Target operativo:** switch **TEST -> LIVE** vinculado a `#187`.
- **Prioridad tecnica:** mantener el flujo de despliegue sin bloqueo por buffers saturados en AI Studio.

## Condiciones de Merge Automatico

El agente debe ejecutar el merge automaticamente solo cuando todas estas condiciones sean verdaderas y verificables:

- El pull request no esta en draft.
- GitHub reporta el estado mergeable como valido o limpio.
- Todos los checks requeridos estan completados en verde (`SUCCESS` / equivalente aprobatorio).
- No existen checks pendientes, en cola o en ejecucion que puedan invalidar el resultado.
- No hay reviews bloqueantes ni cambios solicitados activos.
- La rama base esperada coincide con la configurada para el flujo.

Si cualquiera de estas condiciones falla, el agente debe detener el merge y dejar evidencia del motivo.

## Seguridad y Reporting

- El token de Telegram debe leerse exclusivamente desde entorno seguro, por ejemplo `TELEGRAM_BOT_TOKEN`.
- Nunca se debe versionar ni imprimir el token completo en logs, comentarios, commits o artefactos de CI.
- Cada despliegue debe reportar un evento **Fatality** con payload JSON estable:

```json
{
  "event": "Fatality",
  "deployment": "tryonyou-app",
  "status": "success|failed|blocked",
  "target": "#182/#187",
  "timestamp": "ISO-8601",
  "details": "resumen tecnico sin secretos"
}
```

## Limpieza de Buffers AI Studio

Antes de ejecutar tareas de despliegue, merge o cambio TEST -> LIVE:

- Cerrar sesiones o ejecuciones obsoletas que mantengan el motor ocupado.
- Limpiar buffers temporales generados por ejecuciones anteriores.
- Reintentar solo despues de confirmar que no existe un proceso activo legitimo.
- Registrar el bloqueo como `blocked` si persiste el error `motor ocupado`.

## Regla de Soberania

El protocolo no autoriza bypass de checks, secretos embebidos ni merges sin evidencia. La autonomia total opera dentro de verificaciones tecnicas trazables.

Patente: `PCT/EP2025/067317` - Bajo Protocolo de Soberania V10 - Founder: Ruben
