# Variables de Entorno — Mirror Sanctuary V10

## Configuración en Vercel Dashboard

Accede a: **Vercel → Project Settings → Environment Variables**

### Variables Requeridas

| Variable | Descripción | Ejemplo |
|---|---|---|
| `STRIPE_LINK_SOVEREIGNTY_4_5M` | URL del Payment Link de Stripe para el paquete 4,5M € | `https://buy.stripe.com/xxx` |
| `STRIPE_LINK_SOVEREIGNTY_98K` | URL del Payment Link de Stripe para el paquete 98k € | `https://buy.stripe.com/yyy` |
| `STRIPE_WEBHOOK_SECRET` | Secret del webhook de Stripe (whsec_...) | `whsec_abc123...` |

### Variables Alternativas (compatibilidad)

Las siguientes variables son equivalentes y el sistema las detecta automáticamente:

- `VITE_STRIPE_LINK_SOVEREIGNTY_4_5M` → equivale a `STRIPE_LINK_SOVEREIGNTY_4_5M`
- `VITE_STRIPE_LINK_SOVEREIGNTY_98K` → equivale a `STRIPE_LINK_SOVEREIGNTY_98K`
- `STRIPE_LINK_4_5M_EUR` → equivale a `STRIPE_LINK_SOVEREIGNTY_4_5M`
- `STRIPE_LINK_98K_EUR` → equivale a `STRIPE_LINK_SOVEREIGNTY_98K`

---

## Configuración del Webhook en Stripe

1. Accede a [Stripe Dashboard → Webhooks](https://dashboard.stripe.com/webhooks)
2. Crea un nuevo endpoint con la URL: `https://tryonme-tryonyou-system.vercel.app/api/webhook`
3. Selecciona el evento: `checkout.session.completed`
4. Copia el **Signing Secret** (`whsec_...`) y añádelo como `STRIPE_WEBHOOK_SECRET` en Vercel

---

## Verificación del Sistema

Una vez configuradas las variables, verifica el estado en:

```
GET https://tryonme-tryonyou-system.vercel.app/api/health
```

Respuesta esperada:
```json
{
  "status": "ok",
  "version": "V10.4_Lafayette",
  "stripe_configured": true,
  "stripe_4_5m_set": true,
  "stripe_98k_set": true,
  "webhook_secret_set": true
}
```

---

## Patente

PCT/EP2025/067317 — Mirror Sanctuary V10 Omega
