## Configuracion de Cursor Automation (Cobros Falla)

Objetivo: procesar cobros diarios de falleros con comision fija, control de deuda y anti-duplicados usando `billing/gestor_falla_v9.py`.

### 1) Trigger (Activador)

En Cursor Automation:

1. Haz clic en **Add Trigger**.
2. Selecciona una de estas opciones:
   - **Webhook**: cuando la pasarela de pago envie cada cobro en tiempo real.
   - **Schedule**: para procesar un lote diario (por ejemplo desde Google Sheets o DB).

Para ejecucion diaria a las 09:00:

- **Cron**: `0 9 * * *`
- **RRULE**: `FREQ=DAILY;BYHOUR=9;BYMINUTE=0;BYSECOND=0`

### 2) Instructions (Prompt para Codex 5.3 High)

Copia y pega este bloque en el campo **Instructions**:

```text
Actua como gestor financiero especializado en comisiones de festividades (Falla).
Tu tarea es procesar cada registro de entrada siguiendo estas reglas estrictas:

1. Identificacion: valida el nombre del fallero y el concepto del cobro (cuota, loteria, evento).
2. Calculo de comisiones: aplica un 8% de comision fija sobre el importe bruto recibido.
3. Verificacion de deuda: cruza el pago con la base de datos de Memories para actualizar el saldo pendiente de cada usuario.
4. Registro de transaccion: genera un asiento contable limpio que incluya:
   - Fecha
   - ID de Fallero
   - Importe Bruto
   - Comision Aplicada
   - Neto Resultante
5. Alerta de impagos: si el cobro es menor a la cuota minima establecida, marca la transaccion como "Pendiente de regularizar".

Usa Memories para mantener el historico actualizado y evitar duplicados.

Implementacion de referencia en este repo:
- Script: billing/gestor_falla_v9.py
- Memoria persistente local: billing/falla_memories.json
- Entrada JSON esperada: lista de registros o objeto con clave "registros"
```

### 3) Payload recomendado

Ejemplo por registro:

```json
{
  "fallero_id": "F-001",
  "fallero_nombre": "Pau",
  "concepto": "cuota",
  "importe_bruto": 100.0,
  "transaccion_id": "TX-2026-04-19-0001",
  "fecha": "2026-04-19"
}
```

### 4) Ejecucion local

```bash
python3 billing/gestor_falla_v9.py --input billing/ejemplo_cobros_falla.json --pretty
```

