# Core Engine Jules — Entrega V11

Se ha integrado el **Core Engine** dentro de la arquitectura actual del repositorio, manteniendo el backend serverless en **Python/Flask sobre Vercel** y extendiendo el frontend en **TypeScript** para sesión unificada, trazabilidad, validación financiera y control remoto.

| Área | Implementación |
| --- | --- |
| Trazabilidad total | Persistencia de eventos y sesiones en **Supabase/PostgreSQL** vía `api/core_engine.py` y tablas `core_engine_events`, `core_engine_sessions`, `core_engine_control` |
| Comisión auditable 8% | Registro de `commission_rate`, `commission_basis_eur` y `commission_audit_eur` en cada evento relevante |
| Balance dual | Validación concurrente **Stripe + Qonto** antes de emitir `access_token` |
| Carga 3D progresiva | Placeholder procedural inmediato + carga diferida del GLB final en `RealTimeAvatar.tsx` |
| Kill-Switch | Endpoint oculto remoto con persistencia de estado y sondeo periódico desde el frontend |
| Multi-entorno | Normalización de scopes `personal`, `empresa`, `admin` en backend y cliente |

## Archivos principales modificados

| Archivo | Función |
| --- | --- |
| `api/core_engine.py` | Núcleo del motor: trazabilidad, sesiones, validación Stripe/Qonto, access token, kill-switch |
| `api/index.py` | Exposición de rutas `/api/v1/core/*`, `/api/v1/mirror/snap`, `/api/v1/checkout/perfect-selection` y endpoint oculto de control |
| `src/lib/coreEngineClient.ts` | Gestión unificada de `session_id`, `account_scope`, trazas y solicitud de token 3D |
| `src/lib/julesClient.ts` | Integración del cliente existente con los headers y contratos del Core Engine |
| `src/components/RealTimeAvatar.tsx` | Render progresivo, placeholder inicial, polling de acceso y carga final del modelo |
| `src/divineo/pauV11/loadPauMasterModel.ts` | Nuevo cargador progresivo Three.js con callback de progreso |
| `src/App.tsx` | Sondeo de salud/kill-switch y cableado de eventos de trazabilidad desde la UI |
| `sql/core_engine_supabase.sql` | Esquema SQL para Supabase/PostgreSQL |
| `.env.example` | Variables de entorno requeridas por el Core Engine |

## Endpoints añadidos o reforzados

| Ruta | Método | Propósito |
| --- | --- | --- |
| `/api/v1/core/trace` | `POST` | Registro genérico de eventos auditables |
| `/api/v1/mirror/snap` | `POST` | Registro de escaneo de silueta + respuesta de inventario |
| `/api/v1/checkout/perfect-selection` | `POST` | Registro de interacción de “Mi Selección Perfecta” |
| `/api/v1/core/model-access-token` | `POST` | Emisión condicionada del token 3D tras validación Stripe+Qonto |
| `/api/__jules__/control/kill-switch` | `GET/POST` | Encendido, apagado y consulta remota del espejo |
| `/api/health` | `GET` | Estado operativo, kill-switch y salud del Core Engine |

## Validaciones ejecutadas

| Validación | Resultado |
| --- | --- |
| `npm install` | Correcto |
| `npm run build` | Correcto |
| `python3.11 -m py_compile api/core_engine.py api/index.py api/mirror_digital_make.py api/inventory_engine.py api/shopify_bridge.py api/stripe_webhook_fr.py api/stripe_inauguration.py` | Correcto |
| `git push ... main` | Correcto |
| `npx vercel --prod --yes` | Correcto |

## Publicación

| Elemento | Valor |
| --- | --- |
| Commit | `2a7350e9a64cbb32a6bffef9ee991b83361a91c3` |
| Rama | `main` |
| URL de producción | `https://tryonyou-app-work.vercel.app` |
| URL de inspección Vercel | `https://vercel.com/ruben-espinar-rodriguez-pro/tryonyou-app-work/A3tSrgdbnDapUoSnPgVxkySH8iKu` |

## Configuración pendiente en entorno

Para activar completamente el flujo en producción deben existir las variables documentadas en `.env.example`, en especial las de **Supabase**, **Qonto**, **Stripe FR** y **JULES_KILL_SWITCH_SECRET**.

> Sin `SUPABASE_URL` y `SUPABASE_SERVICE_ROLE_KEY`, el backend conserva fallback local para desarrollo, pero el modo persistente remoto requerido para producción depende de la base de datos configurada.

> Sin `QONTO_API_KEY` y la clave Stripe FR operativa, el endpoint de `model-access-token` responderá correctamente, pero no podrá cualificar positivamente el desbloqueo del modelo 3D.
