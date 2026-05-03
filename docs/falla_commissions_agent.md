# Gestor Falla V9 - cobros, comisiones y Memories

## Trigger recomendado

- **Webhook:** enviar cada cobro recibido a `POST /api/v1/falla/cobros`.
- **Schedule diario:** ejecutar la misma ruta desde el automatizador con la regla
  `FREQ=DAILY;BYHOUR=9;BYMINUTE=0;BYSECOND=0` cuando el origen sea una hoja o base
  de datos.

## Payload minimo

```json
{
  "transaction_id": "pay_123",
  "fallero_id": "F-001",
  "fallero": "Pau",
  "importe_bruto": 100,
  "concepto": "cuota abril",
  "fecha": "2026-05-03",
  "source": "webhook"
}
```

Tambien acepta lotes:

```json
{
  "records": [
    {
      "transaction_id": "pay_123",
      "fallero": "Pau",
      "importe_bruto": 100,
      "concepto": "cuota abril"
    }
  ]
}
```

## Variables de entorno

- `FALLA_COMMISSION_PCT`: comision fija. Acepta `0.08` o `8` para 8%.
- `FALLA_CUOTA_BASE_EUR`: cuota minima para marcar impagos. Default: `50`.
- `FALLA_MEMORIES_PATH`: ruta JSONL de memoria. Default:
  `/tmp/tryonyou_falla/memories.jsonl`.

## Salidas

Cada asiento incluye:

- fecha
- transaction_id
- fallero_id
- fallero
- concepto y validacion de concepto (`cuota`, `loteria`, `evento`)
- importe bruto
- comision aplicada
- neto para la Falla
- estado (`PAGADO` o `PENDIENTE_DE_REGULARIZAR`)
- historico acumulado del fallero

Consultar memoria: `GET /api/v1/falla/memories`.
