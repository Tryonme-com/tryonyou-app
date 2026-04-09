# AGENTS.md

## Cursor Cloud specific instructions

### Project overview

TryOnYou is a React + Vite + Tailwind CSS virtual try-on fashion-tech app (TypeScript frontend, Python FastAPI backend). See `README.md` and `.cursor/rules/` for project lore and protocol context.

### Running services

| Service | Command | Port | Notes |
|---|---|---|---|
| Frontend (Vite dev) | `npm run dev` | 5173 | Proxies `/api` to backend on 8000 |
| Backend (FastAPI) | `uvicorn backend.omega_core:app --reload --port 8000` | 8000 | Local demo API |

Start the backend **before** the frontend so the API proxy works immediately.

### Build

`npm run build` — runs the `prebuild` assertion (`scripts/assert-firebase-applet.mjs` checks `firebase-applet-config.json` projectId) then Vite production build to `dist/`.

### TypeScript

`npx tsc --noEmit` reports `import.meta.env` errors because the repo is missing `src/vite-env.d.ts`. This is a pre-existing issue; Vite build and dev server handle these types internally and work fine.

### Lint / tests

No ESLint config or test framework (Jest/Vitest) is configured in this repo. The primary verification commands are:
- `npx tsc --noEmit` (TypeScript type-check; has known `import.meta.env` errors)
- `npm run build` (Vite production build)

### Environment variables

Copy `.env.example` to `.env`. Most `VITE_*` vars are optional for local dev. Firebase features (auth, analytics, App Check) require `VITE_FIREBASE_API_KEY` + related keys from the Firebase console. Without them the app loads fine but Firebase-dependent features are inactive.

### Python dependencies

Multiple `requirements.txt` files exist:
- `/requirements.txt` — Flask API (Vercel serverless functions)
- `/backend/requirements.txt` — FastAPI local backend (required for dev)
- `/voice_agent/requirements.txt` and `/tryonme-voice-agent/requirements.txt` — optional voice agents
