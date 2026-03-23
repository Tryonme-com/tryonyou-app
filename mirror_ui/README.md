# Mirror UI (desarrollo local)

No sustituye el `index.html` de la raíz del repo (Vercel + `api/index.py`).

```bash
# Terminal 1 — API
cd ..   # raíz tryonyou-app
pip install -r backend/requirements.txt
uvicorn backend.omega_core:app --reload --port 8000

# Terminal 2 — Vite (proxy /api → 8000)
npm install
npm run dev
```

Abre la URL que muestre Vite (p. ej. http://127.0.0.1:5173).
