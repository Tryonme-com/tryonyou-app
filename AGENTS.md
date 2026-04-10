# AGENTS.md

## Cursor Cloud specific instructions

### Servicios principales

| Servicio | Comando | Puerto | Notas |
|----------|---------|--------|-------|
| **Frontend (Vite)** | `npm run dev` | 5173 | SPA React + Tailwind; proxifica `/api` → `localhost:8000` |
| **API (Flask)** | `flask --app api.index run --port 8000` | 8000 | Requiere `PATH` incluya `~/.local/bin` si pip instaló con `--user` |

### Cómo ejecutar

- **Typecheck:** `npx tsc --noEmit`
- **Build:** `npm run build` (ejecuta prebuild assert-firebase-applet antes de vite build)
- **Dev server:** Arrancar Flask API y luego Vite dev. Ver tabla de servicios.
- No existe linter ESLint configurado; el typecheck de TypeScript (`tsc --noEmit`) es la validación estática principal.

### Notas importantes

- El `.env` se crea copiando `.env.example`. Las claves de Stripe/Firebase son opcionales para el desarrollo local básico; la API responde en `/api/health` sin ellas.
- El prebuild (`scripts/assert-firebase-applet.mjs`) valida que `firebase-applet-config.json` exista con `projectId = gen-lang-client-0066102635`. No modificar ese archivo.
- Los voice agents (`tryonme-voice-agent/`, `voice_agent/`) y el backend omega (`backend/`) son servicios independientes con sus propios `requirements.txt`. No son necesarios para la app web principal.
- Flask se instala vía `pip install --user`, por lo que el binario queda en `~/.local/bin`. Asegúrate de que esté en `PATH`.
