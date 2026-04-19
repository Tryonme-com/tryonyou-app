# PROTOCOLO DE AUTONOMÍA TOTAL (HARDENED)

## 1) Notificación de éxito (bot de despliegue)
- Bot operativo: `@tryonyou_deploy_bot`.
- **Nunca** hardcodear tokens en código, docs o commits.
- Token por entorno: `TELEGRAM_BOT_TOKEN` (o `TELEGRAM_TOKEN`), chat por `TELEGRAM_CHAT_ID`.
- Formato de señal recomendado:
  - `evento`: `deploy_success`
  - `branch`: rama actual
  - `commit`: SHA corto
  - `contexto`: `Supercommit_Max`
  - `status`: `ok`

## 2) Despliegue (Supercommit_Max)
- Flujo estándar:
  1. `bash supercommit_max.sh --fast --msg "docs: protocolo soberano"`
  2. `bash supercommit_max.sh --deploy --msg "deploy: bunker + galería web"`
- Sin `VERCEL_TOKEN` en entorno, el despliegue debe fallar de forma explícita y segura.
- Objetivo operativo: sincronizar búnker Oberkampf (75011) con galería web sin forzar push ni acciones destructivas.

## 3) Seguridad financiera (martes 08:00)
- La confirmación de entrada de 450000 EUR **no se automatiza con ejecución ciega**.
- Requerir doble condición:
  1. Evidencia verificable de ingreso (fuente bancaria/contable).
  2. Confirmación manual (`PAYOUT_CONFIRMATION_APPROVED=1`) antes de cualquier acción.
- `Dossier Fatality` solo se activa tras validación positiva de ambas condiciones.

## 4) Estética y robustez Bash
- La galería debe mantener estándar visual 10/10.
- Scripts de shell deben pasar validación (`bash -n`) sin errores.

## 5) Prioridad técnica
- Mantener limpieza de buffers en AI Studio para mitigar error `"motor ocupado"`.
