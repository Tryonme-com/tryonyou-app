# TryOnYou · Divineo

> **Virtual try-on mirror for fashion retail — Zero-Size Protocol V10 Omega**

[![Deploy on Vercel](https://img.shields.io/badge/Deploy-Vercel-black?logo=vercel)](https://tryonyou.app)
[![Patent](https://img.shields.io/badge/Patent-PCT%2FEP2025%2F067317-blue)](https://www.wipo.int)
[![SIREN](https://img.shields.io/badge/SIREN-943%20610%20196-lightgrey)](https://www.societe.com)
[![License](https://img.shields.io/badge/License-Proprietary-red)](#legal)

**Sabrás si te queda bien, antes de comprarlo.**  
Espejo digital en talla real. Sin probadores, sin tallas que hieren. Solo la certeza de verte como eres antes de pagar un solo euro.

---

## Table of Contents

1. [What is TryOnYou?](#what-is-tryonyou)
2. [Key Features](#key-features)
3. [Architecture](#architecture)
4. [Tech Stack](#tech-stack)
5. [Project Structure](#project-structure)
6. [Getting Started](#getting-started)
7. [Environment Variables](#environment-variables)
8. [API Reference](#api-reference)
9. [Deployment](#deployment)
10. [Legal & Intellectual Property](#legal--intellectual-property)

---

## What is TryOnYou?

TryOnYou (brand: **Divineo**) is an AI-powered digital mirror platform that eliminates size anxiety in fashion retail. The core product is a full-screen virtual try-on experience — the customer sees the garment on their real silhouette before paying, with zero dressing-room friction.

**Pilot:** Galeries Lafayette × Balmain, Paris · Launch: May 2026  
**Headquarters:** 27 Rue de Argenteuil, 75001 Paris, France

### The Zero-Size Protocol

Traditional sizing (S / M / L / XL) is replaced by a **biometrically certified single size** derived from a real-time body scan. The system emits a checkout with quantity 1 on the Zero-Size variant — no "buy two just in case", no returns from indecision.

- **Anti-accumulation** — only one certified size per customer journey.  
- **Single-size certitude** — the cart never contains redundant size variants.  
- **Zero devoluciones** — eliminating returns caused by size uncertainty is the primary sustainability KPI.

---

## Key Features

| Feature | Description |
|---|---|
| 🪞 **Digital Mirror (The Snap)** | Full-screen body-scan overlay driven by MediaPipe biometrics (<150 ms latency). Press **P.A.U.** to capture the silhouette and trigger Jules orchestration. |
| 👗 **Zero-Size Checkout** | Non-Stop Shopping flow: one tap → instant Shopify / Amazon checkout with no size selection step. |
| 🎟️ **VIP Reservation** | QR-code cabin reservation for Galeries Lafayette courtesy fitting (Divineo protocol). |
| 🧬 **Biometric Fit Engine** | MediaPipe-powered body landmark detection with `drape_bias` / `tension_bias` / `aligned` verdicts. |
| 📋 **Lead Capture & Beta Waitlist** | Hero email form + bunker orchestrator. Leads persisted to SQLite, forwarded to Make.com webhooks. |
| 🤖 **Jules Finance Orchestration** | Backend AI agent managing treasury, Bpifrance liquidity, and multi-channel checkout routing. |
| 🔒 **Sovereign Data** | Biometric measurements never exposed in client UI. All data under GDPR-compliant French entity (SIREN 943 610 196). |
| 🛒 **Multi-channel Commerce** | Shopify Admin API (draft orders) + Amazon SP-API (LWA) + Stripe payment links. |

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      Vercel Edge / CDN                          │
│  ┌──────────────────────────┐   ┌──────────────────────────┐   │
│  │   React 18 + TypeScript  │   │  Python Serverless API   │   │
│  │      (Vite build)        │   │     (api/index.py)       │   │
│  │                          │   │                          │   │
│  │  App.tsx                 │   │  /api/health             │   │
│  │  OfrendaOverlay          │   │  /api/v1/leads           │   │
│  │  LeadVaultGate           │   │  /api/v1/mirror/snap     │   │
│  │  CrystalToast            │   │  /api/v1/checkout/...    │   │
│  │  PaymentTerminal         │   │  /api/vetos_core_inference│  │
│  │  useOmegaAnalytics       │   │  /api/bunker_full_orch.. │   │
│  └──────────┬───────────────┘   └──────────┬───────────────┘   │
│             │  fetch()                      │                   │
└─────────────┼──────────────────────────────┼───────────────────┘
              │                              │
    ┌─────────▼──────────────────────────────▼─────────┐
    │              Integration Layer                    │
    │  Make.com · Shopify · Amazon · Stripe · Telegram  │
    │  Google Sheets · Slack · ElevenLabs · Gemini AI   │
    └──────────────────────────────────────────────────┘
```

### Core Modules

| Module | Location | Responsibility |
|---|---|---|
| **Robert Engine** | `backend/omega_core.py` | Biometric processing, MediaPipe orchestration |
| **Jules Finance** | `api/index.py` + `src/lib/julesClient.ts` | Treasury, checkout routing, mirror snap |
| **Vetos Core** | `backend/vetos_core_inference.py` | AI inference, lead scoring, bunker sync |
| **Peacock Core** | `backend/peacock_core.py` + `src/lib/peacock_core.ts` | Brand engine, inventory matching |
| **Shopify Bridge** | `backend/shopify_bridge.py` | Draft order creation, Zero-Size variant |
| **Amazon Bridge** | `backend/amazon_bridge.py` | SP-API / LWA catalog lookup |
| **SACMUSEUM Engine** | `backend/sack_museum_engine.py` | Physical store (75001) orchestration |
| **Make Mirror Bridge** | `backend/make_mirror_bridge.py` | Make.com webhook relay |

---

## Tech Stack

**Frontend**

- [React 18](https://react.dev) + [TypeScript](https://www.typescriptlang.org)
- [Vite 7](https://vitejs.dev) (build tool & dev server)
- CSS custom properties — no external UI library

**Backend (Python serverless, Vercel)**

- Python 3.11+, FastAPI-compatible serverless handlers
- MediaPipe (biometric processing, <150 ms latency)
- SQLite (lead persistence)

**Integrations**

| Service | Purpose |
|---|---|
| **Make.com** | Automation webhooks for leads, mirrors, and orders |
| **Shopify Admin API** | Draft order creation (Zero-Size variant, no talla step) |
| **Amazon SP-API (LWA)** | Product catalog + affiliate checkout links |
| **Stripe** | Payment links (sovereignty tiers, sovereignty 98 K€) |
| **Telegram** | Operational signals (VIP fatality, bunker alerts) |
| **Slack** | SMTP replacement, operational notifications |
| **ElevenLabs** | Voice agent (Serena / Lily persona) |
| **Google Gemini AI** | Oracle scripts, unification layer |
| **Vercel** | Frontend + serverless API deployment |

---

## Project Structure

```
tryonyou-app/
├── api/                        # Python serverless API (Vercel)
│   ├── index.py                # Main router: health, leads, mirror, checkout
│   ├── shopify_bridge.py       # Shopify Admin API draft orders
│   ├── amazon_bridge.py        # Amazon SP-API / affiliate links
│   ├── vetos_core_inference.py # AI inference + bunker sync
│   ├── peacock_core.py         # Brand/inventory engine
│   ├── make_mirror_bridge.py   # Make.com relay
│   └── sack_museum_engine.py   # Physical SACMUSEUM (75001) logic
├── backend/
│   ├── omega_core.py           # Robert Engine core
│   └── requirements.txt
├── src/
│   ├── App.tsx                 # Root component (hero, ofrenda, P.A.U.)
│   ├── components/
│   │   ├── OfrendaOverlay.tsx  # Zero-Size action overlay
│   │   ├── LeadVaultGate.tsx   # Lead capture gate
│   │   ├── CrystalToast.tsx    # Notification toast
│   │   └── biometrics/         # MediaPipe components
│   ├── lib/
│   │   ├── julesClient.ts      # Jules API client (health, snap)
│   │   ├── peacock_core.ts     # Brand engine client
│   │   ├── fabricFitComparator.ts
│   │   └── licenseGate.ts
│   ├── hooks/
│   │   └── useOmegaAnalytics.js
│   ├── pages/
│   │   └── payment-terminal.tsx
│   └── app/
│       └── page.tsx            # Galeries Lafayette × Balmain entry
├── design/
│   └── STORE_LAYOUT.md         # SACMUSEUM floor plan (Zero-Perchas)
├── public/
│   └── videos/                 # P.A.U. transparent video assets
├── .env.example                # All environment variable templates
├── vercel.json                 # Vercel deployment config
├── vite.config.ts
├── tsconfig.json
└── package.json
```

---

## Getting Started

### Prerequisites

- **Node.js** ≥ 18  
- **Python** ≥ 3.11  
- A [Vercel](https://vercel.com) account (for deployment)

### 1. Clone & install

```bash
# Install frontend dependencies
npm install

# Install Python API dependencies
pip install -r backend/requirements.txt
```

### 2. Configure environment

```bash
cp .env.example .env
# Edit .env and fill in required variables (see Environment Variables below)
```

At minimum you need:
```env
MAKE_WEBHOOK_URL=https://hook.eu2.make.com/...
SHOPIFY_STORE_DOMAIN=your-store.myshopify.com
SHOPIFY_ADMIN_ACCESS_TOKEN=shpat_...
SHOPIFY_ZERO_SIZE_VARIANT_ID=...
```

### 3. Run locally

```bash
# Start frontend dev server (http://localhost:5173)
npm run dev

# Run Python API locally (separate terminal)
cd api && python index.py
```

### 4. Build for production

```bash
npm run build
# Output: dist/
```

---

## Environment Variables

Copy `.env.example` to `.env`. Full documentation is in the example file. Key groups:

| Group | Variables | Notes |
|---|---|---|
| **Public domain** | `TRYONYOU_PUBLIC_DOMAIN` | `tryonyou.app` |
| **Make.com webhooks** | `MAKE_WEBHOOK_URL`, `MAKE_ESPEJO_WEBHOOK_URL`, `TRYONYOU_LEAD_WEBHOOK_URL` | Custom webhook URLs from Make scenarios |
| **Leads DB** | `DIVINEO_LEADS_DB_PATH`, `LEADS_DB_PATH` | SQLite paths for lead persistence |
| **Shopify** | `SHOPIFY_ADMIN_ACCESS_TOKEN`, `SHOPIFY_STORE_DOMAIN`, `SHOPIFY_ZERO_SIZE_VARIANT_ID` | Admin API for draft orders |
| **Amazon** | `AMAZON_PERFECT_ASIN`, `SP_API_LWA_CLIENT_ID`, `SP_API_LWA_CLIENT_SECRET` | SP-API catalog lookup |
| **Stripe** | `STRIPE_LINK_SOVEREIGNTY_4_5M`, `STRIPE_LINK_SOVEREIGNTY_98K` | Payment link templates |
| **Telegram** | `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID` | Operational alerts |
| **Slack** | `SLACK_WEBHOOK_URL` | SMTP replacement notifications |
| **ElevenLabs** | `ELEVENLABS_API_KEY`, `ELEVENLABS_VOICE_ID` | Voice agent (Serena/Lily) |
| **Gemini AI** | `GOOGLE_STUDIO_API_KEY` | Oracle/oracle scripts |
| **Vercel** | `VERCEL_TOKEN` | CLI deployments |
| **Jules / Checkout** | `JULES_API_KEY_V10`, `CHECKOUT_PRIMARY_CHANNEL` | `shopify` or `amazon` |

---

## API Reference

Base URL: `https://tryonyou.app/api`

### `GET /health`

Returns Jules engine status and protocol metadata.

```json
{
  "ok": true,
  "service": "omega",
  "siren": "943610196",
  "patente": "PCT/EP2025/067317",
  "product_lane": "tryonyou_v10_omega",
  "protocol": "zero_size"
}
```

### `POST /v1/leads`

Capture a lead intent.

```json
// Request
{
  "intent": "reserve | combo | save | share | selection",
  "source": "ofrenda_v10",
  "protocol": "zero_size",
  "revenue_validation": 7500,
  "code": "optional_referral_code"
}
```

### `POST /v1/mirror/snap`

The Snap — trigger Jules orchestration with biometric fabric verdict.

```json
// Request
{
  "ping": true,
  "fabric_sensation": "Préférence drapé / Préférence tenue / aligned",
  "fabric_fit_verdict": "drape_bias | tension_bias | aligned",
  "code": "optional"
}
// Response
{
  "status": "success",
  "jules_msg": "Le drapé répond avec élégance...",
  "inventory_match": {
    "match_absolute": "BALMAIN_DRESS_001",
    "garment_id": "...",
    "brand_line": "Balmain"
  }
}
```

### `POST /v1/checkout/perfect-selection`

Non-Stop Shopping — Zero-Size checkout.

```json
// Request
{
  "fabric_sensation": "drape_bias",
  "protocol": "zero_size",
  "shopping_flow": "non_stop_card",
  "anti_accumulation": true,
  "single_size_certitude": true
}
// Response
{
  "emotional_seal": "Votre sélection parfaite...",
  "checkout_primary_url": "https://...",
  "checkout_shopify_url": "https://...",
  "checkout_amazon_url": "https://..."
}
```

### `POST /vetos_core_inference`

Bunker sync — AI lead scoring and sovereign data validation.

### `POST /bunker_full_orchestrator`

Beta waitlist registration with Make.com relay and priority scoring.

---

## Deployment

### Vercel (recommended)

```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
vercel --prod
```

The `vercel.json` at the root configures:
- Static frontend served from `dist/`
- Python serverless functions from `api/`

Set all environment variables in the Vercel dashboard under **Settings → Environment Variables**.

### Key deployment checklist

- [ ] All `MAKE_*` webhook URLs configured in Vercel env  
- [ ] `SHOPIFY_ADMIN_ACCESS_TOKEN` + `SHOPIFY_ZERO_SIZE_VARIANT_ID` set  
- [ ] `DIVINEO_LEADS_DB_PATH` pointing to a writable path (or use Make relay)  
- [ ] `TELEGRAM_BOT_TOKEN` + `TELEGRAM_CHAT_ID` for ops alerts  
- [ ] `JULES_API_KEY_V10` set for checkout routing  

---

## Legal & Intellectual Property

| Field | Value |
|---|---|
| **Founder** | Rubén Espinar Rodríguez |
| **Entity** | TryOnYou Paris |
| **SIREN** | 943 610 196 |
| **SIRET** | 94361019600017 |
| **Headquarters** | 27 Rue de Argenteuil, 75001 Paris, France |
| **International Patent** | PCT/EP2025/067317 |
| **Status** | Operative · Commercial pilot May 2026 |

All source code, protocols, and brand assets in this repository are the exclusive property of **Rubén Espinar Rodríguez / TryOnYou Paris**. Unauthorized reproduction, distribution, or commercial use is strictly prohibited.

*Zero-Size™, Divineo™, and the P.A.U. protocol are proprietary marks under PCT/EP2025/067317.*

---

*Este repositorio es la fuente de verdad única para el piloto comercial en Galeries Lafayette.*
