# Configuración recomendada — Cobros Falla (Codex 5.3 High)

## 1) Triggers (Activadores)

Haz clic en **Add Trigger** y selecciona la fuente de datos:

- **Webhook**: si recibes una notificación por cada pago (app o pasarela).
- **Schedule**: si quieres revisar una hoja (Google Sheets) o base de datos cada día.

Regla de frecuencia sugerida:

`FREQ=DAILY;BYHOUR=9;BYMINUTE=0;BYSECOND=0`

---

## 2) Instructions (texto para pegar en el prompt)

Actúa como gestor financiero especializado en comisiones de festividades (Falla).
Tu tarea es procesar cada registro de entrada siguiendo estas reglas estrictas:

1. Identificación: valida el nombre del fallero y el concepto del cobro (cuota, lotería, evento).
2. Cálculo de comisiones: aplica un 8% de comisión fija sobre el importe bruto recibido.
3. Verificación de deuda: cruza el pago con la base de datos de Memories para actualizar el saldo pendiente de cada usuario.
4. Registro de transacción: genera un asiento contable limpio que incluya Fecha, ID de Fallero, Importe Bruto, Comisión Aplicada y Neto Resultante.
5. Alerta de impagos: si el cobro es menor a la cuota mínima establecida, marca la transacción como "Pendiente de regularizar".
6. Antiduplicados: rechaza cobros repetidos usando transaccion_id o una clave hash equivalente.

Usa las herramientas de Memories para mantener el histórico actualizado y asegurar que no existan duplicados en los cobros.

---

## 3) Referencia de implementación (Python)

```python
import datetime


class GestorFallaV9:
    def __init__(self, comision_pct=0.08, cuota_base=50.0):
        self.comision_pct = comision_pct
        self.cuota_base = cuota_base
        # Simulación de "Memories"
        self.registro_memoria = []

    def ejecutar_cobro(self, nombre, bruto, concepto):
        fecha = datetime.date.today().strftime("%d/%m/%Y")

        comision = round(bruto * self.comision_pct, 2)
        neto = round(bruto - comision, 2)
        estado = "PAGADO" if bruto >= self.cuota_base else "DEUDA PENDIENTE"

        asiento = {
            "fecha": fecha,
            "fallero": nombre.upper(),
            "concepto": concepto,
            "bruto": f"{bruto}€",
            "comision_8pct": f"{comision}€",
            "neto_falla": f"{neto}€",
            "estado": estado,
        }
        self.registro_memoria.append(asiento)
        return asiento
```
