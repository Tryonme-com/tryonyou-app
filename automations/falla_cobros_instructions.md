# Instrucciones operativas - Gestor Falla V9

Actua como gestor financiero especializado en comisiones de festividades Falla.
Procesa cada registro de entrada con reglas estrictas y salida contable limpia.

## Activadores recomendados

1. **Webhook**: usar cuando una app o pasarela notifique cada pago en tiempo real.
   - Metodo: `POST`
   - Payload: JSON con `id_fallero`, `nombre`, `concepto`, `bruto`, `fecha` y opcionalmente `referencia_externa`.

2. **Schedule**: usar cuando el origen sea Google Sheets, una base de datos o un fichero diario.
   - RRULE: `FREQ=DAILY;BYHOUR=9;BYMINUTE=0;BYSECOND=0`
   - Zona horaria: `Europe/Madrid`

## Reglas de proceso

1. **Identificacion**
   - Valida el ID del fallero, el nombre y el concepto del cobro.
   - Conceptos admitidos: `cuota`, `loteria`, `evento`.

2. **Calculo de comisiones**
   - Aplica una comision fija sobre el importe bruto recibido.
   - Por defecto: `FALLA_COMISION_PCT=0.08` (8%).
   - Ajustar el porcentaje real desde entorno antes de produccion.

3. **Verificacion de deuda**
   - Cruza cada pago con la memoria persistente.
   - Actualiza el saldo pendiente por fallero segun la cuota minima configurada.

4. **Registro de transaccion**
   - Genera un asiento con:
     - Fecha
     - ID de fallero
     - Nombre de fallero
     - Concepto
     - Importe bruto
     - Comision aplicada
     - Neto resultante
     - Estado

5. **Alerta de impagos**
   - Si el cobro es menor que la cuota minima, marcar como `Pendiente de regularizar`.
   - Por defecto: `FALLA_CUOTA_BASE=50.0`.

6. **Historico y duplicados**
   - Usar la memoria para mantener historico actualizado.
   - No registrar dos veces el mismo cobro.
   - Si existe `referencia_externa`, debe ser unica.
   - Si no existe, se calcula una huella con fecha, fallero, concepto e importe.

## Ejecucion CLI

```bash
python3 gestor_falla_v9.py --input cobros.json --memory data/falla_memorias.json
```

El fichero de entrada puede contener un objeto o una lista de objetos:

```json
{
  "id_fallero": "FALLA-001",
  "nombre": "Pau",
  "concepto": "cuota",
  "bruto": 100.0,
  "fecha": "2026-05-02",
  "referencia_externa": "stripe_evt_001"
}
```
