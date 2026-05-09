/**
 * TRYONYOU — Procedural Garment Overlays.
 *
 * Generates SVG silhouettes (gold on transparent, with luminous edge glow)
 * adapted to garment type, then converts to HTMLImageElement for canvas drawImage.
 *
 * Typology:
 *   robe         → long flowing dress
 *   ensemble     → jacket + trousers (two-piece)
 *   chemise      → blouse / shirt
 *   pantalon     → trousers
 *   jupe         → skirt
 *   manteau      → coat
 *   foulard      → scarf
 *   accessoire   → accessory tile
 *
 * The SVG is rendered with a viewport of 400×600 (portrait, garment ratio ~2/3).
 * Canvas pipeline scales it to (shoulderW × X) using naturalWidth/Height.
 */

import type { Garment } from "@/lib/catalog";

const GOLD = "#C9A84C";
const GOLD_DIM = "#8a7536";

function svgWrapper(inner: string): string {
  // viewBox 400×600 (portrait). The garment is centered horizontally.
  // Defs include gradient + glow filter (used by all paths).
  return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 600" width="400" height="600">
  <defs>
    <linearGradient id="g" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="${GOLD}" stop-opacity="0.95"/>
      <stop offset="55%" stop-color="${GOLD}" stop-opacity="0.78"/>
      <stop offset="100%" stop-color="${GOLD_DIM}" stop-opacity="0.62"/>
    </linearGradient>
    <linearGradient id="g2" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%" stop-color="${GOLD_DIM}" stop-opacity="0.5"/>
      <stop offset="50%" stop-color="${GOLD}" stop-opacity="0.9"/>
      <stop offset="100%" stop-color="${GOLD_DIM}" stop-opacity="0.5"/>
    </linearGradient>
    <filter id="glow" x="-20%" y="-20%" width="140%" height="140%">
      <feGaussianBlur stdDeviation="3" result="b"/>
      <feMerge>
        <feMergeNode in="b"/>
        <feMergeNode in="SourceGraphic"/>
      </feMerge>
    </filter>
  </defs>
  <g filter="url(#glow)">${inner}</g>
</svg>`;
}

function robeSVG(): string {
  // Long elegant dress: shoulders 200→ flares at waist→hem.
  return svgWrapper(`
    <path d="M 140 60
             L 260 60
             Q 270 70 268 95
             L 280 130
             Q 295 160 300 220
             L 310 360
             Q 320 480 340 580
             L 60 580
             Q 80 480 90 360
             L 100 220
             Q 105 160 120 130
             L 132 95
             Q 130 70 140 60 Z"
          fill="url(#g)" stroke="${GOLD}" stroke-width="1.2" stroke-opacity="0.85"/>
    <path d="M 200 95 L 200 575" stroke="${GOLD}" stroke-width="0.8" stroke-opacity="0.4" stroke-dasharray="3 5"/>
    <path d="M 90 360 Q 200 400 310 360" fill="none" stroke="${GOLD}" stroke-width="0.6" stroke-opacity="0.35"/>
  `);
}

function ensembleSVG(): string {
  // Jacket + trousers, two parts.
  return svgWrapper(`
    <!-- jacket -->
    <path d="M 130 60
             L 270 60
             Q 282 75 278 110
             L 305 145
             Q 320 175 318 230
             L 318 290
             L 282 290
             L 260 270
             L 200 270
             L 140 270
             L 118 290
             L 82 290
             L 82 230
             Q 80 175 95 145
             L 122 110
             Q 118 75 130 60 Z"
          fill="url(#g)" stroke="${GOLD}" stroke-width="1.2" stroke-opacity="0.85"/>
    <path d="M 200 65 L 200 270" stroke="${GOLD_DIM}" stroke-width="0.8" stroke-opacity="0.7"/>
    <circle cx="200" cy="160" r="2" fill="${GOLD}"/>
    <circle cx="200" cy="200" r="2" fill="${GOLD}"/>
    <circle cx="200" cy="240" r="2" fill="${GOLD}"/>

    <!-- trousers -->
    <path d="M 110 305
             L 290 305
             L 285 350
             L 270 580
             L 215 580
             L 205 360
             L 195 360
             L 185 580
             L 130 580
             L 115 350 Z"
          fill="url(#g)" stroke="${GOLD}" stroke-width="1.1" stroke-opacity="0.85"/>
    <path d="M 200 305 L 200 360" stroke="${GOLD_DIM}" stroke-width="0.7" stroke-opacity="0.5"/>
  `);
}

function chemiseSVG(): string {
  return svgWrapper(`
    <path d="M 130 60
             L 270 60
             Q 282 75 278 110
             L 305 145
             Q 318 175 318 220
             L 320 280
             L 80 280
             L 82 220
             Q 82 175 95 145
             L 122 110
             Q 118 75 130 60 Z"
          fill="url(#g)" stroke="${GOLD}" stroke-width="1.2" stroke-opacity="0.85"/>
    <path d="M 200 65 L 200 280" stroke="${GOLD_DIM}" stroke-width="0.8" stroke-opacity="0.6"/>
    <path d="M 80 280 L 320 280" stroke="${GOLD}" stroke-width="0.8" stroke-opacity="0.5"/>
  `);
}

function pantalonSVG(): string {
  return svgWrapper(`
    <path d="M 130 60
             L 270 60
             L 280 110
             L 280 580
             L 215 580
             L 205 220
             L 195 220
             L 185 580
             L 120 580
             L 120 110 Z"
          fill="url(#g)" stroke="${GOLD}" stroke-width="1.2" stroke-opacity="0.85"/>
    <path d="M 200 60 L 200 220" stroke="${GOLD_DIM}" stroke-width="0.7" stroke-opacity="0.6"/>
    <path d="M 130 110 L 270 110" stroke="${GOLD}" stroke-width="0.8" stroke-opacity="0.4"/>
  `);
}

function jupeSVG(): string {
  return svgWrapper(`
    <path d="M 145 60
             L 255 60
             Q 268 70 270 95
             L 295 200
             Q 320 380 350 580
             L 50 580
             Q 80 380 105 200
             L 130 95
             Q 132 70 145 60 Z"
          fill="url(#g)" stroke="${GOLD}" stroke-width="1.2" stroke-opacity="0.85"/>
    <path d="M 80 380 Q 200 420 320 380" fill="none" stroke="${GOLD}" stroke-width="0.6" stroke-opacity="0.4"/>
  `);
}

function manteauSVG(): string {
  return svgWrapper(`
    <path d="M 110 50
             L 290 50
             Q 305 65 300 110
             L 330 160
             Q 345 200 343 280
             L 340 380
             Q 335 480 320 580
             L 80 580
             Q 65 480 60 380
             L 57 280
             Q 55 200 70 160
             L 100 110
             Q 95 65 110 50 Z"
          fill="url(#g)" stroke="${GOLD}" stroke-width="1.4" stroke-opacity="0.9"/>
    <path d="M 200 55 L 200 580" stroke="${GOLD_DIM}" stroke-width="1" stroke-opacity="0.65"/>
    <circle cx="195" cy="180" r="2.5" fill="${GOLD}"/>
    <circle cx="195" cy="260" r="2.5" fill="${GOLD}"/>
    <circle cx="195" cy="340" r="2.5" fill="${GOLD}"/>
    <circle cx="195" cy="420" r="2.5" fill="${GOLD}"/>
    <path d="M 110 110 Q 130 130 160 130 L 240 130 Q 270 130 290 110" fill="none" stroke="${GOLD}" stroke-width="0.8" stroke-opacity="0.55"/>
  `);
}

function foulardSVG(): string {
  return svgWrapper(`
    <path d="M 130 80
             Q 200 60 270 80
             Q 290 110 285 160
             Q 270 240 260 320
             Q 240 400 200 460
             Q 160 400 140 320
             Q 130 240 115 160
             Q 110 110 130 80 Z"
          fill="url(#g2)" stroke="${GOLD}" stroke-width="1.1" stroke-opacity="0.85"/>
    <path d="M 200 70 L 200 460" stroke="${GOLD_DIM}" stroke-width="0.7" stroke-opacity="0.5" stroke-dasharray="4 6"/>
  `);
}

function accessoireSVG(): string {
  return svgWrapper(`
    <rect x="120" y="120" width="160" height="200" rx="12"
          fill="url(#g)" stroke="${GOLD}" stroke-width="1.4" stroke-opacity="0.9"/>
    <path d="M 145 120 Q 145 90 200 90 Q 255 90 255 120"
          fill="none" stroke="${GOLD}" stroke-width="2" stroke-opacity="0.85"/>
    <rect x="180" y="200" width="40" height="8" rx="2" fill="${GOLD_DIM}"/>
  `);
}

const SVG_BUILDERS: Record<string, () => string> = {
  robe: robeSVG,
  ensemble: ensembleSVG,
  chemise: chemiseSVG,
  pantalon: pantalonSVG,
  jupe: jupeSVG,
  manteau: manteauSVG,
  foulard: foulardSVG,
  accessoire: accessoireSVG,
};

export function svgForGarment(g: Garment): string {
  const builder = SVG_BUILDERS[g.type] ?? robeSVG;
  return builder();
}

/** Convert an SVG string to a Data URL usable as <img src=...>. */
export function svgToDataUrl(svg: string): string {
  // Use encodeURIComponent for safety with non-ASCII chars.
  return `data:image/svg+xml;charset=utf-8,${encodeURIComponent(svg)}`;
}

/** Async loader returning HTMLImageElement once decoded. */
export function loadOverlayImage(garment: Garment): Promise<HTMLImageElement> {
  return new Promise((resolve, reject) => {
    const img = new Image();
    img.onload = () => resolve(img);
    img.onerror = () => reject(new Error(`overlay load failed for ${garment.id}`));
    img.src = svgToDataUrl(svgForGarment(garment));
  });
}

/** Same SVG used as catalog vignette (scaled CSS-side). */
export function catalogVignetteUrl(garment: Garment): string {
  return svgToDataUrl(svgForGarment(garment));
}
