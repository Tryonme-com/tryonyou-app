# Automatizacion de cobros Falla V9

Este flujo procesa cobros de falleros desde un webhook o desde una ejecucion programada
diaria. El contrato se mantiene estable para Make.com, Google Sheets o cualquier pasarela
que envie JSON.

## Trigger recomendado

- **Webhook**: usar `POST /api/v1/falla/cobros` cuando la pasarela notifique un pago.
- **Schedule**: ejecutar el mismo POST por cada fila pendiente de Google Sheets o base de datos.
- Frecuencia sugerida si se usa cron/automation: `FREQ=DAILY;BYHOUR=9;BYMINUTE=0;BYSECOND=0`.

## Variables

- `FALLA_COMISION_PCT`: porcentaje de comision. Acepta `0.08` o `8`. Por defecto: `0.08`.
- `FALLA_CUOTA_BASE`: cuota minima para marcar regularizacion. Por defecto: `50.00`.
- `FALLA_MEMORY_PATH`: ruta JSON de memoria. Por defecto: `/tmp/tryonyou_falla_memories.json`.

## Payload

```json
{
  "transaction_id": "stripe_evt_123",
  "fallero_id": "FALLERO-PAU",
  "fallero": "Pau",
  "concepto": "Cuota Abril",
  "importe_bruto": 100,
  "fecha": "2026-05-04"
}
```

Campos alias aceptados:

- `nombre`, `name` o `customer_name` para `fallero`.
- `concept` para `concepto`.
- `bruto`, `importe`, `amount` o `amount_eur` para `importe_bruto`.
- `id_transaccion`, `payment_id` o `id` para `transaction_id`.

Conceptos validos: `cuota`, `loteria`, `evento` (tambien con texto posterior, por ejemplo
`Cuota Abril`).

## Respuesta

```json
{
  "status": "ok",
  "asiento": {
    "fecha": "2026-05-04",
    "transaction_id": "stripe_evt_123",
    "fallero_id": "FALLERO-PAU",
    "fallero": "PAU",
    "concepto": "Cuota Abril",
    "importe_bruto_eur": "100.00EUR",
    "comision_pct": "8.00",
    "comision_aplicada_eur": "8.00EUR",
    "neto_falla_eur": "92.00EUR",
    "estado": "PAGADO"
  }
}
```

Si se recibe de nuevo el mismo `transaction_id`, la respuesta devuelve `status:
"duplicate"` y no escribe un segundo asiento.

Para auditar totales:

```http
GET /api/v1/falla/cobros/resumen
```
