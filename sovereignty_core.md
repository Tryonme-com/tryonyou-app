# PROTOCOLO DE AUTONOMIA TOTAL

## Objetivo

Este protocolo coordina la autonomia operativa del agente PAU para:

- Liquidacion de 51,988.50 EUR asociada al issue #182.
- Switch TEST->LIVE asociado al issue #187.
- Merge automatico de PRs solo cuando las verificaciones de GitHub esten en verde.
- Reporte "Fatality" por Telegram sin exponer secretos.
- Limpieza de buffers de AI Studio para reducir el error "motor ocupado".

Patente: PCT/EP2025/067317  
Bajo Protocolo de Soberania V10 - Founder: Ruben

## Reglas De Seguridad

1. No se declara una liquidacion como ejecutada sin evidencia bancaria, Qonto o Stripe verificable.
2. No se ejecuta switch LIVE con claves `sk_test_`, `pk_test_` ni endpoints de prueba.
3. No se imprime ni versiona ningun token. Telegram usa solo `TELEGRAM_BOT_TOKEN` o `TELEGRAM_TOKEN` junto con `TELEGRAM_CHAT_ID`.
4. El merge automatico requiere que el PR no este en draft, que apunte a `main` y que todos los checks requeridos esten en estado satisfactorio.
5. Si falta credencial, evidencia o check verde, el agente debe parar la accion irreversible y reportar el motivo.

## Gate De Merge Automatico

Antes de mergear un PR:

1. Consultar estado de GitHub del PR.
2. Verificar que `mergeStateStatus` no indique conflicto o bloqueo.
3. Validar que cada check requerido este en `SUCCESS` o equivalente aprobado. Los checks en `IN_PROGRESS`, `FAILURE`, `ERROR`, `CANCELLED` o `TIMED_OUT` bloquean el merge.
4. Ejecutar las validaciones locales relevantes del repo:
   - `npm run typecheck`
   - `npm run build`
   - tests Python especificos si el cambio toca API, tesoreria o Stripe.
5. Solo despues de esos pasos, ejecutar merge con token autorizado.

Si el PR ya aparece como `MERGED`, no repetir el merge: registrar el SHA de merge y continuar con el reporte.

## Target #182: Liquidacion 51,988.50 EUR

La liquidacion se considera pendiente hasta que exista una de estas evidencias:

- Confirmacion bancaria o Qonto con referencia verificable.
- Payout Stripe LIVE con `livemode=true` y estado compatible con fondos liquidados.
- Registro local de evidencia aprobado por `FinancialGuard` o guard equivalente.

El agente puede monitorizar y formatear el estado, pero no debe simular cobros como reales.

## Target #187: Switch TEST->LIVE

El cambio TEST->LIVE solo queda autorizado si:

- La cuenta esta verificada.
- Existen credenciales LIVE configuradas en entorno.
- El flujo rechaza claves de prueba cuando el modo operativo exige LIVE.
- Los endpoints mantienen payloads JSON estables para Make.com y consumidores existentes.

## Reporte Telegram Fatality

El reporte debe enviarse unicamente si existen credenciales en entorno:

```bash
TELEGRAM_BOT_TOKEN=...
TELEGRAM_CHAT_ID=...
```

Formato minimo del reporte:

```text
FATALITY DEPLOYMENT REPORT
PR: <numero>
Estado: <MERGED|BLOCKED|FAILED>
Checks: <resumen>
Merge SHA: <sha si existe>
Patente: PCT/EP2025/067317
```

Si faltan token o chat id, el agente debe dejar constancia del bloqueo sin inventar envio.

## Limpieza De Buffers AI Studio

Para evitar el error "motor ocupado":

1. Cerrar sesiones duplicadas de AI Studio antes de lanzar una nueva sincronizacion.
2. Mantener un unico prompt canonico mediante `GOOGLE_AI_STUDIO_PROMPT_URL`.
3. Evitar bucles de generacion concurrentes sobre el mismo prompt.
4. Registrar el intento fallido y reintentar solo despues de liberar la sesion activa.
5. No borrar `node_modules` ni artefactos productivos salvo indicacion explicita o error de dependencias confirmado.

## Estado De Este Protocolo

Este archivo es el contrato operativo. La ejecucion real depende de checks verdes, credenciales disponibles y evidencias verificables en cada run.
