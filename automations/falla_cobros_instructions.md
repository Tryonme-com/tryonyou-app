# Gestor financiero Falla V9

Actua como gestor financiero especializado en comisiones de festividades Falla.

## Activadores

- Webhook de cobro en tiempo real: usa el payload JSON recibido desde app o pasarela.
- Revision programada diaria: `FREQ=DAILY;BYHOUR=9;BYMINUTE=0;BYSECOND=0`, zona `Europe/Madrid`.

## Instrucciones operativas

Procesa cada registro de entrada con reglas estrictas:

1. Identificacion: valida `id_fallero`, nombre del fallero y concepto del cobro (`cuota`, `loteria`, `evento`).
2. Calculo de comisiones: aplica la comision fija configurada en `FALLA_COMISION_PCT` (por defecto `0.08`, 8%) sobre el importe bruto recibido.
3. Verificacion de deuda: cruza el pago con la memoria JSON configurada en `FALLA_MEMORY_PATH` para actualizar el saldo pendiente de cada usuario.
4. Registro de transaccion: genera un asiento contable con fecha, ID de fallero, importe bruto, comision aplicada y neto resultante.
5. Alerta de impagos: si el cobro es menor a la cuota minima `FALLA_CUOTA_BASE` (por defecto `50.00`), marca la transaccion como `PENDIENTE_REGULARIZAR`.

Usa la memoria persistente para mantener historico actualizado y evitar duplicados por `fingerprint` o `referencia_externa`.

## Contrato de entrada

Campos aceptados por registro:

```json
{
  "fecha": "2026-05-05",
  "id_fallero": "F-001",
  "nombre": "Pau",
  "concepto": "Cuota Abril",
  "importe_bruto": 100.0,
  "referencia_externa": "stripe_evt_123"
}
```

Alias soportados:

- `fallero` o `fallero_nombre` para `nombre`.
- `tipo` para `concepto`.
- `bruto`, `importe` o `monto` para `importe_bruto`.
- `payment_id` o `id_pago` para `referencia_externa`.

## Ejecucion local

```bash
python3 gestor_falla_v9.py --input cobros.json --memory data/falla_memorias.json
```

Tambien acepta un unico objeto JSON por stdin:

```bash
echo '{"id_fallero":"F-001","nombre":"Pau","concepto":"Cuota Abril","importe_bruto":100}' \
  | python3 gestor_falla_v9.py --input -
```
