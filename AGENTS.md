# AGENTS.md — TryOnYou / Espejo Digital Soberano

## Cursor Cloud specific instructions

### Project overview

TryOnYou is a React + Vite + Tailwind virtual try-on fashion-tech SPA with Python backend components: Flask handlers under `api/` run serverlessly on Vercel, while the FastAPI app under `backend/` is used for local/demo development. See `README.md` and the `.cursor/rules/` files for full product context.

### Quick reference

| Task | Command |
|---|---|
| Install JS deps | `npm install` |
| Install Python deps | `pip install -r requirements.txt` |
| Dev server (frontend) | `npm run dev` → http://localhost:5173 |
| TypeScript check | `npm run typecheck` |
| Production build | `npm run build` |
| Python tests | `python3 -m unittest discover -s tests -p 'test_*.py'` |
| Full dry-run pipeline | `bash scripts/deployall.sh --dry` |

### Non-obvious caveats

- **pip binaries not on PATH by default.** After `pip install`, Flask and httpx binaries land in `/home/ubuntu/.local/bin`. Prepend that to `$PATH` if you need to call them directly (`export PATH="/home/ubuntu/.local/bin:$PATH"`).
- **`firebase-applet-config.json` prebuild check.** The `npm run build` (and `npm run prebuild`) runs `scripts/assert-firebase-applet.mjs`, which validates that `projectId` in `firebase-applet-config.json` equals `gen-lang-client-0066102635`. Do not change that file unless re-provisioning Firebase.
- **Vite proxies `/api` to `http://127.0.0.1:8000`.** If you need API endpoints locally, first install the backend-specific Python dependencies with `pip install -r backend/requirements.txt`, then start the FastAPI backend with `uvicorn backend.omega_core:app --reload --port 8000`. The frontend renders independently without the backend.
- **Environment variables are optional for dev.** Firebase, Stripe, ElevenLabs, and other SaaS integrations require env vars (see `.env.example`), but the frontend loads and renders without them. Firebase init gracefully degrades when keys are missing.
- **Python tests pass** with zero external dependencies beyond `requirements.txt`.
- **Commit messages** must include `@CertezaAbsoluta`, `@lo+erestu`, `PCT/EP2025/067317`, and `Bajo Protocolo de Soberanía V10 - Founder: Rubén` (see `.cursor/rules/agente-pau-tryonyou.mdc`).
