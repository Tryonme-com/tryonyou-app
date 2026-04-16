# INVOICE REPORT — Auditoría de Liquidación V10/V11

Fecha de generación (UTC): 2026-04-16
Patente: PCT/EP2025/067317

## 1) Fuentes auditadas (solo evidencias del repositorio)

- `registro_pagos_hoy.csv`: 11 transacciones en estado `CONFIRMADO` por **40.000,00 €** totales.
- `billing/FACTURA_RUBEN_LAFAYETTE.md` y `billing/PENDIENTES_COBRO_SIREN_943610196.md`: setup fee oficial **7.500,00 € HT / 9.000,00 € TTC**, marcado como pendiente.
- `production_manifest.json`: importe inauguración Stripe configurado en **12.500,00 €** (configuración de checkout, no liquidación confirmada).
- `pilot_analytics.json`: evento Lafayette con `revenue_potential = 12.500 €` (potencial, no cobro confirmado).

## 2) Cálculo de comisión extra V11 (8%)

Base usada: volumen confirmado en `registro_pagos_hoy.csv`.

- Volumen confirmado: **40.000,00 €**
- Comisión V11 (8%): **3.200,00 €**

## 3) Desglose solicitado (documento de presión)

### Hito 2

- Referencia contractual/narrativa solicitada: **100.000,00 €**
- Estado en repositorio: **referencia objetivo**, no se encontró justificante de cobro liquidado en las fuentes auditadas.

### Setup Fees

- Setup fee: **7.500,00 € HT** (equivalente **9.000,00 € TTC** en factura oficial).
- Estado: **pendiente** según `billing/PENDIENTES_COBRO_SIREN_943610196.md`.

### Comisiones V11

- Comisión extra 8% sobre volumen confirmado auditado: **3.200,00 €**.

### MRR

- MRR solicitado: **450,00 €**.
- Estado en repositorio: **sin registro explícito verificable** de línea MRR de 450€ en los logs/archivos auditados.

## 4) Totales de presión (escenarios)

### Escenario A — solo datos confirmados por log/estado

- Setup fee pendiente (HT): **7.500,00 €**
- Comisión V11 confirmada (8%): **3.200,00 €**
- **Total bloqueado mínimo verificable: 10.700,00 €** (HT, sin mezclar TTC).

### Escenario B — incluyendo objetivo Hito 2 y MRR solicitado

- Hito 2 objetivo: **100.000,00 €**
- Setup fee (HT): **7.500,00 €**
- Comisión V11 (8%): **3.200,00 €**
- MRR solicitado: **450,00 €**
- **Total de presión solicitado: 111.150,00 €**

> Nota de sinceridad: este escenario B combina objetivos/solicitudes con datos confirmados; no debe presentarse como “cobro ya validado” sin extracto contable/bancario adicional.

## 5) Riesgos de interpretación

- Existen importes de deuda distintos en manifestos (`16.200 € TTC` y `33.200 € TTC`) que no están reconciliados en una única fuente contable.
- El evento de `12.500 €` aparece como potencial/configuración (checkout), no como pago asentado.
- Los logs runtime en `logs/` están casi vacíos en este entorno, por lo que no hay prueba adicional de liquidaciones Lafayette en producción real.
