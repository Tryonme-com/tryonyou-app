# Gestor de cobros de Falla

`logic.gestion_falla` procesa registros provenientes de un webhook, Make.com,
una exportación de Google Sheets o una tarea programada. Aplica una comisión
del 8 % por defecto, actualiza el saldo pendiente y evita duplicados.

## Activador

- Webhook: enviar el registro de la pasarela con una `referencia` estable.
- Schedule: para las 09:00 cada día, usar `FREQ=DAILY;BYHOUR=9;BYMINUTE=0;BYSECOND=0`
  o su equivalente cron `0 9 * * *`. La zona horaria debe configurarse
  explícitamente en el orquestador.

Payload compatible:

```json
{
  "nombre": "Pau",
  "fallero_id": "F-001",
  "bruto": 100,
  "concepto": "Cuota Abril",
  "referencia": "pi_123",
  "fecha": "2026-04-10"
}
```

También admite una lista o `{"registros": [...]}`. Para Make.com se conservan
los alias `monto`/`importe`, `tipo` y `payment_id`.

## Ejecución

```bash
python3 -m logic.gestion_falla --input cobros.json
```

Para recibir el JSON por entrada estándar:

```bash
printf '%s' '{"nombre":"Pau","bruto":100,"concepto":"Cuota Abril","referencia":"pi_123"}' \
  | python3 -m logic.gestion_falla
```

Configuración:

- `FALLA_COMISION_PCT=0.08`
- `FALLA_CUOTA_MINIMA_EUR=50.00`
- `FALLA_MEMORIES_PATH=data/falla_memories.json`
- `FALLA_LEDGER_PATH=logs/falla_cobros.jsonl`

La memoria JSON es la fuente de verdad. El libro JSONL se sincroniza desde ella
en cada operación. Un reintento con la misma `referencia` devuelve
`"duplicado": true` y no genera un segundo asiento.

Patente: PCT/EP2025/067317
Bajo Protocolo de Soberanía V10 - Founder: Rubén
