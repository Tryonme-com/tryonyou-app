# Sincronización del Búnker — Inmunidad Técnica V11

## Estado de sincronización (implementado)

- **Mirror principal + fallback local:** `src/App.tsx` entra en modo preview controlado cuando `/api/health` no responde y aplica bloqueo soberano si `payment_verified=false`.
- **Canal espejo externo (Make):** `api/mirror_digital_make.py` soporta `MIRROR_AUTONOMY_MODE` (`primary`, `degraded`, `sanctuary`).
- **Cola local resiliente:** cuando Make no está disponible o el modo es degradado/sanctuary, los eventos se encolan en `logs/mirror_autonomy_queue.jsonl`.
- **Estado consultable por API:** nueva ruta `GET /api/v1/mirror/autonomy/status` (y alias `/v1/mirror/autonomy/status`) devuelve modo activo, webhook configurado y tamaño de cola.

## Contrato operativo recomendado

1. `MIRROR_AUTONOMY_MODE=primary` en operación normal.
2. `MIRROR_AUTONOMY_MODE=degraded` en incidente parcial de conectividad.
3. `MIRROR_AUTONOMY_MODE=sanctuary` en caída/bloqueo del plano principal.
4. Monitorizar `queued_events` del endpoint de estado para replay operacional.

---

*Documento técnico de auditoría y ejecución. Patente PCT/EP2025/067317.*
