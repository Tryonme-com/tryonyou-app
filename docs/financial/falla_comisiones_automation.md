# Automatizacion de comisiones Falla V9

Contrato operativo para activar cobros de falleros desde cron, webhook, CSV o JSON.

## Activadores recomendados

- **Webhook**: entrada directa desde Stripe, Make.com u otra pasarela cuando se confirma
  un pago.
- **Schedule**: revision diaria de una hoja exportada a CSV/JSON o una base intermedia.
  Frecuencia sugerida: `FREQ=DAILY;BYHOUR=9;BYMINUTE=0;BYSECOND=0`.

## Instrucciones del agente

Actua como gestor financiero especializado en comisiones de festividades Falla.

1. Valida nombre de fallero y concepto (`cuota`, `loteria`, `evento`).
2. Aplica una comision fija sobre el importe bruto recibido.
3. Cruza cada pago con la memoria JSON para actualizar saldo pendiente.
4. Genera asiento contable con fecha, ID de fallero, bruto, comision y neto.
5. Marca `PENDIENTE DE REGULARIZAR` si el bruto es inferior a la cuota base.
6. Deduplica siempre por `id_transaccion` antes de registrar.

## Ejecucion CLI

Cobro directo:

```bash
python3 gestor_falla_v9.py \
  --nombre "Pau" \
  --bruto 100 \
  --concepto "Cuota Abril" \
  --id-transaccion pay_001 \
  --fecha 2026-05-06 \
  --pretty
```

Procesado programado desde CSV/JSON:

```bash
python3 gestor_falla_v9.py \
  --input cobros_falla.csv \
  --memoria falla_memories.json \
  --comision-pct 8 \
  --cuota-base 50 \
  --pretty
```

## Campos de entrada soportados

| Campo canonico | Alias aceptados |
| --- | --- |
| `nombre` | `fallero`, `name` |
| `bruto` | `importe_bruto`, `importe_eur`, `amount_eur` |
| `concepto` | `tipo_cobro` |
| `id_transaccion` | `transaction_id`, `stripe_id` |
| `fallero_id` | `id_fallero` |
| `fecha` | `fecha_hora`, `created_at` |

La memoria se guarda por defecto en `data/falla_memorias.json` o en la ruta indicada por
`FALLA_MEMORY_PATH`. Tambien se acepta `FALLA_MEMORIA_PATH` como alias legacy.
