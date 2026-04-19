# TRYONYOU — B2B landing rewrite deployment report

The landing page was rewritten as a **B2B conversion-first experience** in `src/App.tsx` while preserving the existing operational logic around **PAU**, **Ofrenda**, **Firebase/App Check**, health polling, fit event handling, and backend interaction helpers.

| Area | Result |
|---|---|
| `salesCopy.ts` | Unchanged, reused as requested |
| `src/App.tsx` | Rewritten to use the existing design system and multilingual B2B sales copy |
| `src/App.css` | Extended with scroll reveal, manifesto glow, animated counter glow, and hero border glow |
| Header | Sticky header with nav, locale switcher, and demo CTA |
| Landing sections | Hero, problem, solution, benefits, technology, trust/metrics, demo form, final CTA, ethics, manifesto bottom, footer |
| Existing components preserved | `OfrendaOverlay`, `PauFloatingGuide`, `PreScanHook`, `RealTimeAvatar`, PAU orb |
| Demo form | Posts to `/api/v1/leads` |
| Motion effects | Ambient particles, reveal on scroll, animated metric counters |

## Build and publish

| Step | Outcome |
|---|---|
| `npm install` | Completed successfully |
| `npm run build` | Completed successfully |
| Git commit | `9e0e77f` — `feat: B2B conversion-first landing page with premium luxury UX` |
| `git push origin main` | Successful |
| `git push lvt main` | Remote already up to date after push path resolved |
| Vercel deployment trigger | Successful |
| Deployment ID | `dpl_8Zco5zZfn1KaukpLq6XjagmL4GsB` |

## Endpoint verification

| Endpoint | Result |
|---|---|
| `https://tryonyou.app/api/health` | Responded with `ok: true` |
| `https://tryonyou.app/api/v1/core/trace` | GET request responded with `405 Method Not Allowed` |

> The `/api/v1/core/trace` response indicates that the route is present but does not accept the GET method used by the verification command.
