# SECURITY REPORT — Production Hardening Audit

Fecha: 2026-07-24  
Rama: `cursor/soberania-black-box-ac17`

## 1) Files changed

- `api/index.py`
- `index.html`
- `package.json`
- `package-lock.json`
- `src/App.tsx`
- `src/lib/firebaseApplet.ts`
- `src/main.tsx`
- `src/vite-env.d.ts` (new)
- `src/bootstrap/mediapipeFitBridge.ts` (new)
- `src/bootstrap/sovereignLockdown.ts` (new)
- `public/assets/gold_swirl_v11.gif` (new)
- `vercel.json`

## 2) Vulnerabilities fixed

### Authorization hardening
- Removed client-side default authorization fallback in app flow.
- Removed all runtime `window.UserCheck`/`isAuthorized: true` fallback paths from production frontend (`src/*`).
- Authorization now starts locked and only opens after successful backend health validation.

### Kill-switch fail-closed
- If backend health fails, mirror stays locked (`mirrorPoweredOn=false`).
- Added degraded/maintenance message instead of enabling mirror when health API is unreachable.

### CORS hardening
- Removed wildcard CORS behaviour in backend runtime.
- `api/index.py` now resolves allowed origins from `ALLOWED_ORIGINS`.
- Localhost origins are only auto-allowed in development environment.
- Removed wildcard CORS header from `vercel.json`.

### TypeScript strict compliance
- Added `src/vite-env.d.ts` with explicit environment/window typings.
- Fixed strict typing issues to make `npx tsc --noEmit` pass.
- No strict mode downgrade applied.

### Performance and event pressure
- Replaced aggressive district polling loop with event-driven updates.
- Implemented visibility-aware backend health polling (`setTimeout` + `visibilitychange`).
- Added throttling for `tryonyou:fit` UI updates.
- Migrated MediaPipe frame/business logic from HTML script to TS module with throttled dispatch.

### Hybrid architecture cleanup
- `index.html` now only bootstraps React.
- Business/runtime logic moved into React-side bootstrap modules.

### Asset integrity
- Added missing `public/assets/gold_swirl_v11.gif` to remove unresolved asset warning in build.

### Dependency security
- Ran `npm audit fix` and reduced npm vulnerabilities to zero in current lockfile.

## 3) Remaining risks

1. Repository still contains legacy/scripted files outside production runtime (`src`, `api`, `index`, `vercel`) with risky patterns such as `document.documentElement.innerHTML` and `window.UserCheck`.  
   - Current matches found in:
     - `sovereign_lock_fr_v11.py`
     - `architect_sovereign_final.py`
     - `.cursor/rules/*` helper rule files
2. Frontend main bundle is still large (~622 KB emitted JS chunk), so additional code-splitting/perf work may be needed for strict web-performance budgets.
3. CORS policy now requires explicit `ALLOWED_ORIGINS` in production; missing env configuration can block browser clients until set.

## 4) Production readiness

Status: **READY WITH ENV REQUIREMENT**

Required production env:
- `ALLOWED_ORIGINS` (comma-separated trusted origins)

Behaviour after hardening:
- Auth path defaults locked.
- Backend health failure keeps app in degraded fail-closed mode.
- Build and strict type checks pass.

## 5) Validation executed

- `npm install`
- `npm audit fix`
- `npm run lint`
- `npx tsc --noEmit`
- `npm run build`
- `python3 -m unittest tests.test_sovereign_black_box tests.test_sovereign_sale tests.test_stripe_lafayette`

## 6) Score (/100)

**91/100**

Rationale:
- + Strong improvements in auth defaults, fail-closed behavior, CORS, strict typing, and build integrity.
- + Production commands pass end-to-end.
- - Residual legacy risky patterns remain in non-runtime helper/legacy scripts.
- - Bundle size remains high for performance-critical deployments.
