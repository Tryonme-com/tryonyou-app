# Gestor de Cobros Falla V9 - Configuracion de Automation

Este documento deja preparado el flujo para **Codex 5.3 High** con trigger diario y/o webhook.

## 1) Triggers (Activadores)

En la automatizacion, pulsa **Add Trigger** y configura una de estas opciones:

### Opcion A - Webhook (recomendada para cobro en tiempo real)
- Tipo: `Webhook`
- Uso: cuando la pasarela/app envia una notificacion en cada pago.
- Payload esperado minimo:
  - `id_fallero`
  - `nombre`
  - `concepto` (`cuota`, `loteria`, `evento`)
  - `importe_bruto`
  - `fecha` (opcional)
  - `transaccion_id` (recomendado para evitar duplicados)

### Opcion B - Schedule (revision diaria)
- Tipo: `Schedule`
- Regla RRULE: `FREQ=DAILY;BYHOUR=9;BYMINUTE=0;BYSECOND=0`
- Cron equivalente: `0 9 * * *`
- Uso: revisar cada dia una hoja (Google Sheets) o base de datos.

---

## 2) Instructions (texto listo para pegar)

Copia y pega este bloque en el campo **Instructions**:

```text
Actúa como gestor financiero especializado en comisiones de festividades (Falla).
Tu tarea es procesar cada registro de entrada siguiendo estas reglas estrictas:

1. Identificación: Valida el nombre del fallero y el concepto del cobro (cuota, lotería, evento).
2. Cálculo de Comisiones: Aplica un [X]% de comisión fija sobre el importe bruto recibido (sustituye X por tu porcentaje real).
3. Verificación de Deuda: Cruza el pago con la base de datos de 'Memories' para actualizar el saldo pendiente de cada usuario.
4. Registro de Transacción: Genera un asiento contable limpio que incluya: Fecha, ID de Fallero, Importe Bruto, Comisión Aplicada y Neto Resultante.
5. Alerta de Impagos: Si el cobro es menor a la cuota mínima establecida, marca la transacción como "Pendiente de regularizar".

Usa las herramientas de 'Memories' para mantener el histórico actualizado y asegurar que no existan duplicados en los cobros.
```

---

## 3) Implementacion Python recomendada

La implementacion productiva ya esta en:

- `billing/gestor_falla_v9.py`

Incluye:
- validacion de conceptos y datos de entrada,
- comision fija configurable,
- control de deuda pendiente por fallero,
- estado `"Pendiente de regularizar"` cuando corresponde,
- deduplicacion por `transaccion_id`.

---

## 4) Uso rapido local

```bash
python3 billing/gestor_falla_v9.py
```

Para integrar en automatizaciones, importa `GestorFallaV9` y ejecuta `ejecutar_cobro(...)` por cada registro entrante.
