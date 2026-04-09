# AGENTS.md

## Cursor Cloud specific instructions

### Product overview

TryOnYou is a luxury fashion virtual try-on SPA (React + Vite + Tailwind) with a Python FastAPI backend. It is deployed on Vercel (frontend static + Python serverless functions). Patent PCT/EP2025/067317.

### Services

| Service | Command | Port | Notes |
|---|---|---|---|
| **Frontend (Vite)** | `npm run dev` | 5173 | Proxies `/api` requests to backend on port 8000 |
| **Backend (FastAPI)** | `uvicorn backend.omega_core:app --reload --port 8000` | 8000 | Health: `GET /health`, Snap: `POST /api/snap` |

### Running the dev environment

1. Start backend: `uvicorn backend.omega_core:app --reload --port 8000`
2. Start frontend: `npm run dev`
3. Open `http://localhost:5173/?postal=75009` (the `postal` param activates the PAU pilot mode)

### Build

- `npm run build` — runs `prebuild` (validates `firebase-applet-config.json` projectId) then Vite production build.

### TypeScript

- `npx tsc --noEmit` reports errors about `import.meta.env` because there is no `src/vite-env.d.ts` referencing `vite/client` types. These errors do **not** block the Vite build or dev server — Vite handles `import.meta.env` natively. This is a known gap in the repo.

### Lint

- No ESLint config is present in the repo. TypeScript strict mode (`tsconfig.json`) is the primary static check.

### Tests

- No automated test framework is configured. Testing is manual via browser and API calls.

### Environment variables

- See `.env.example` for the full list. No `.env` file is committed.
- Firebase, Stripe, Make.com, and other external service keys are optional for local dev — the app runs without them (features that depend on those keys simply won't work).
- The `prebuild` step (`scripts/assert-firebase-applet.mjs`) requires `firebase-applet-config.json` with `projectId` set to `gen-lang-client-0066102635`. This file is committed and does not need changes.

### Python path

- `uvicorn` and `fastapi` install to `~/.local/bin`. Ensure this is on `PATH`:
  ```
  export PATH="$HOME/.local/bin:$PATH"
  ```

### Crontab note

- The workspace rules mention `0 9 * * * /usr/bin/python3 /ruta/a/tu/daily_manager.py` — this is a production cron reference, not relevant for local dev setup.
