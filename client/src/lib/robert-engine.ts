/**
 * TRYONYOU — Robert Physics Renderer
 * © 2025-2026 Rubén Espinar Rodríguez — All Rights Reserved
 * Patent: PCT/EP2025/067317 — 22 Claims Protected
 * System: TRYONYOU–ABVETOS–ULTRA–PLUS–ULTIMATUM
 *
 * Robert Engine: Real-time garment physics rendering on canvas.
 * Uses fabric drapeCoefficient, weightGSM, elasticityPct, and recoveryPct
 * to simulate realistic garment behavior over the user's body.
 *
 * NOT a static image overlay — Robert recalculates every frame.
 */

// ─── Fabric Physics Profile (mirrors shared/patent.ts) ───
export interface RobertFabricParams {
  drapeCoefficient: number;   // 0-1 (0=stiff, 1=liquid)
  weightGSM: number;          // grams per square meter
  elasticityPct: number;      // 0-100
  recoveryPct: number;        // 0-100
  frictionCoefficient: number; // 0-1
}

// ─── Body Anchor Points ───
export interface BodyAnchors {
  cx: number;         // center X
  shoulderY: number;  // shoulder Y
  hipY: number;       // hip Y
  shoulderW: number;  // shoulder width px
  angle: number;      // torso tilt radians
  hasBody: boolean;   // true if MediaPipe detected
}

// ─── Fabric physics lookup for the 5 pilot garments ───
export const PILOT_FABRIC_PHYSICS: Record<string, RobertFabricParams> = {
  eg001: { drapeCoefficient: 0.92, weightGSM: 85,  elasticityPct: 12, recoveryPct: 88, frictionCoefficient: 0.28 }, // Seda Elástica
  eg002: { drapeCoefficient: 0.55, weightGSM: 220, elasticityPct: 5,  recoveryPct: 72, frictionCoefficient: 0.45 }, // Lana Ligera
  eg003: { drapeCoefficient: 0.78, weightGSM: 340, elasticityPct: 8,  recoveryPct: 65, frictionCoefficient: 0.62 }, // Terciopelo Líquido
  eg004: { drapeCoefficient: 0.48, weightGSM: 180, elasticityPct: 4,  recoveryPct: 45, frictionCoefficient: 0.52 }, // Algodón Premium
  eg005: { drapeCoefficient: 0.42, weightGSM: 195, elasticityPct: 15, recoveryPct: 92, frictionCoefficient: 0.38 }, // Mix Industrial
};

// ═══════════════════════════════════════════════════════════════
// ROBERT DRAPE SIMULATION
// Applies per-frame physics to the garment overlay:
// 1. Gravity pull (weight → vertical stretch)
// 2. Drape wave (drapeCoefficient → sinusoidal hem deformation)
// 3. Elasticity breathing (elasticityPct → micro-scale oscillation)
// 4. Body-responsive alpha (closer fit = higher opacity)
// ═══════════════════════════════════════════════════════════════

/**
 * Calculate the LAFAYETTE_FACTOR dynamically based on fabric physics.
 * Stiffer fabrics (low drape) → wider silhouette (more structured).
 * Liquid fabrics (high drape) → narrower, body-hugging silhouette.
 */
export function calculateLafayetteFactor(fabric: RobertFabricParams): number {
  // Base factor 2.2, adjusted by drape
  // High drape (0.9+) → factor ~1.9 (body-hugging)
  // Low drape (0.3-) → factor ~2.5 (structured/wide)
  const drapePull = fabric.drapeCoefficient * 0.4;
  return 2.2 + (0.5 - drapePull);
}

/**
 * Calculate gravity-induced vertical stretch.
 * Heavier fabrics pull down more, elongating the garment.
 */
export function calculateGravityStretch(fabric: RobertFabricParams, torsoH: number): number {
  // Normalize weight: 0 at 50gsm, 1 at 400gsm
  const weightNorm = Math.min(1, Math.max(0, (fabric.weightGSM - 50) / 350));
  // Heavy fabrics add up to 15% extra length
  return torsoH * (1 + weightNorm * 0.15);
}

/**
 * Calculate per-frame drape wave offset for the hem.
 * Liquid fabrics have larger, slower waves. Stiff fabrics barely move.
 * Returns an array of wave offsets for N points along the hem.
 */
export function calculateDrapeWave(
  fabric: RobertFabricParams,
  time: number,
  garmentW: number,
  numPoints: number = 8
): number[] {
  const amplitude = fabric.drapeCoefficient * 6; // max ±6px for liquid fabrics
  const frequency = 0.003 - fabric.drapeCoefficient * 0.001; // slower for liquid
  const phase = time * frequency;

  const offsets: number[] = [];
  for (let i = 0; i < numPoints; i++) {
    const x = (i / (numPoints - 1)) * garmentW;
    const wave = Math.sin(phase + x * 0.02) * amplitude;
    // Add weight-based sag in the center
    const centerDist = Math.abs(i - numPoints / 2) / (numPoints / 2);
    const gravitySag = (1 - centerDist) * (fabric.weightGSM / 100) * 2;
    offsets.push(wave + gravitySag);
  }
  return offsets;
}

/**
 * Calculate dynamic opacity based on fit certainty and fabric properties.
 * Higher fit score → more opaque (garment "settles" on body).
 * While recalculating (<95%) → slight transparency pulse.
 */
export function calculateDynamicAlpha(
  fitScore: number,
  fabric: RobertFabricParams,
  time: number
): number {
  const baseAlpha = 0.85;
  const fitBonus = fitScore > 95 ? 0.10 : 0;

  if (fitScore < 95) {
    // Pulsing transparency while Robert recalculates
    const pulse = Math.sin(time * 0.004) * 0.08;
    return Math.max(0.65, baseAlpha + pulse);
  }

  // Settled: full opacity with slight fabric-dependent shimmer
  const shimmer = fabric.frictionCoefficient < 0.3
    ? Math.sin(time * 0.002) * 0.03  // Silk shimmer
    : 0;

  return Math.min(0.95, baseAlpha + fitBonus + shimmer);
}

/**
 * Calculate elasticity-based micro-oscillation.
 * Elastic fabrics "breathe" with the body — subtle width pulsation.
 */
export function calculateElasticityBreathing(
  fabric: RobertFabricParams,
  time: number
): number {
  const breathAmplitude = fabric.elasticityPct / 100 * 0.02; // max 2% width change
  return 1 + Math.sin(time * 0.003) * breathAmplitude;
}

// ═══════════════════════════════════════════════════════════════
// ROBERT RENDER FUNCTION — Called every frame from TryOn.tsx
// Replaces the simple drawImage with physics-aware rendering
// ═══════════════════════════════════════════════════════════════

// ─── Garment length factor by type (relative to torsoH = shoulder → hip distance) ───
// A factor of 1.0 means the garment ends exactly at the hip line.
// A factor of 2.4 means it extends 2.4x the torso height below the shoulders (e.g. long dress).
const GARMENT_LENGTH_FACTORS: Record<string, number> = {
  top: 1.05,        // short top, ends just past hip
  chemise: 1.20,    // shirt/blouse, slight overhang past hip
  ensemble: 2.30,   // jacket + trousers (full body)
  veste: 1.35,      // jacket, mid-hip
  manteau: 2.50,    // coat, long
  robe: 2.40,       // dress, long
  jupe: 1.85,       // skirt, mid-calf (anchored at hip, but we draw from shoulders for simplicity)
  pantalon: 2.30,   // trousers (drawn from waist line, but we use shoulders as anchor)
  combinaison: 2.40,// jumpsuit
  foulard: 0.90,    // scarf, sits over shoulders / chest
};
function lengthFactorFor(type: string): number {
  return GARMENT_LENGTH_FACTORS[type] ?? 1.30;
}

export function robertRenderGarment(
  ctx: CanvasRenderingContext2D,
  img: HTMLImageElement,
  anchors: BodyAnchors,
  garmentId: string,
  fitScore: number,
  isAccessory: boolean,
  canvasW: number,
  _canvasH: number,
  garmentType: string = "robe"
): void {
  const fabric = PILOT_FABRIC_PHYSICS[garmentId];
  if (!fabric) {
    // Fallback: simple render
    simpleRender(ctx, img, anchors, isAccessory, canvasW, _canvasH, garmentType);
    return;
  }

  const now = Date.now();
  const { cx, shoulderY, hipY, shoulderW, angle, hasBody } = anchors;
  const torsoH = Math.max(60, hipY - shoulderY); // guard against zero/negative

  if (isAccessory) {
    // Accessories: physics-lite (just gravity sway). Bag sits at the hip line, slightly outboard.
    const bagW = (hasBody ? shoulderW : canvasW * 0.22) * 0.55;
    const ar = img.naturalHeight / img.naturalWidth;
    const bagH = bagW * ar;
    const sway = Math.sin(now * 0.002) * (fabric.weightGSM / 100) * 2;
    const bagX = cx + (hasBody ? shoulderW * 0.55 : canvasW * 0.10) + sway;
    const bagY = hipY - bagH * 0.20; // hangs from hip, mostly below

    ctx.save();
    ctx.globalAlpha = calculateDynamicAlpha(fitScore, fabric, now);
    ctx.drawImage(img, bagX, bagY, bagW, bagH);
    ctx.restore();
    return;
  }

  // ─── GARMENT PHYSICS RENDERING ───
  // CRITICAL: height is derived from the BODY (torsoH × lengthFactor), NOT from the image AR.
  // This guarantees the garment hangs from shoulders DOWN through the hips and below, never above.
  const lafayetteFactor = calculateLafayetteFactor(fabric);
  const elasticBreath = calculateElasticityBreathing(fabric, now);
  const garmentW = shoulderW * lafayetteFactor * elasticBreath;
  const targetH = torsoH * lengthFactorFor(garmentType);
  const gravityH = calculateGravityStretch(fabric, targetH);
  // Anchor the TOP of the garment slightly above shoulder line (collar/neckline ~6% of torso).
  const collarLift = torsoH * 0.06;
  const drawY = shoulderY - collarLift;
  const alpha = calculateDynamicAlpha(fitScore, fabric, now);

  ctx.save();
  ctx.translate(cx, drawY);
  if (hasBody && Math.abs(angle) > 0.01) ctx.rotate(angle);

  ctx.globalCompositeOperation = 'source-over';
  ctx.globalAlpha = alpha;

  // ─── DRAPE DEFORMATION via mesh warp (simplified) ───
  // We split the garment into vertical strips and apply wave offsets
  const strips = 12;
  const stripW = garmentW / strips;
  const drapeWave = calculateDrapeWave(fabric, now, garmentW, strips);
  const srcStripW = img.naturalWidth / strips;

  for (let i = 0; i < strips; i++) {
    const srcX = i * srcStripW;
    const dstX = -garmentW / 2 + i * stripW;

    // Wave offset increases toward bottom (hem)
    const waveOffset = drapeWave[i] || 0;

    // Gravity stretch: bottom strips stretch more
    const stripStretch = 1 + (i > strips * 0.6 ? (fabric.weightGSM / 1000) * 0.1 : 0);

    ctx.drawImage(
      img,
      srcX, 0, srcStripW, img.naturalHeight,  // source
      dstX, waveOffset * 0.3, stripW, gravityH * stripStretch  // destination with physics
    );
  }

  // ─── DRAPE SHADOW (weight-based) ───
  if (fabric.weightGSM > 200) {
    const shadowIntensity = Math.min(0.15, (fabric.weightGSM - 200) / 1000);
    const shadowGrad = ctx.createLinearGradient(
      -garmentW / 2, gravityH * 0.7,
      -garmentW / 2, gravityH
    );
    shadowGrad.addColorStop(0, `rgba(0, 0, 0, 0)`);
    shadowGrad.addColorStop(1, `rgba(0, 0, 0, ${shadowIntensity})`);
    ctx.fillStyle = shadowGrad;
    ctx.fillRect(-garmentW / 2, gravityH * 0.7, garmentW, gravityH * 0.3);
  }

  // ─── SILK HIGHLIGHT (low friction fabrics) ───
  if (fabric.frictionCoefficient < 0.3) {
    const highlightX = Math.sin(now * 0.001) * garmentW * 0.3;
    const highlightGrad = ctx.createRadialGradient(
      highlightX, gravityH * 0.3, 0,
      highlightX, gravityH * 0.3, garmentW * 0.4
    );
    highlightGrad.addColorStop(0, 'rgba(255, 255, 255, 0.06)');
    highlightGrad.addColorStop(1, 'rgba(255, 255, 255, 0)');
    ctx.fillStyle = highlightGrad;
    ctx.fillRect(-garmentW / 2, 0, garmentW, gravityH);
  }

  // ─── RECALCULATION INDICATOR ───
  if (fitScore < 95) {
    // Subtle scanning line effect while Robert recalculates
    const scanLineY = ((now % 2000) / 2000) * gravityH;
    ctx.strokeStyle = 'rgba(197, 164, 109, 0.15)';
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.moveTo(-garmentW / 2, scanLineY);
    ctx.lineTo(garmentW / 2, scanLineY);
    ctx.stroke();
  }

  ctx.restore();
}

// ─── Simple fallback render (no physics) ───
// Same anchoring rules as the physics renderer: garment height is body-driven, never image-AR-driven.
function simpleRender(
  ctx: CanvasRenderingContext2D,
  img: HTMLImageElement,
  anchors: BodyAnchors,
  isAccessory: boolean,
  canvasW: number,
  _canvasH: number,
  garmentType: string = "robe"
): void {
  const { cx, shoulderY, hipY, shoulderW, hasBody, angle } = anchors;
  const ar = img.naturalHeight / img.naturalWidth;
  const torsoH = Math.max(60, hipY - shoulderY);

  if (isAccessory) {
    const bagW = (hasBody ? shoulderW : canvasW * 0.22) * 0.55;
    const bagH = bagW * ar;
    const bagX = cx + (hasBody ? shoulderW * 0.55 : canvasW * 0.10);
    const bagY = hipY - bagH * 0.20;
    ctx.save();
    ctx.globalAlpha = 0.88;
    ctx.drawImage(img, bagX, bagY, bagW, bagH);
    ctx.restore();
  } else {
    const garmentW = shoulderW * 2.2;
    const garmentH = torsoH * lengthFactorFor(garmentType); // body-driven, not AR-driven
    const collarLift = torsoH * 0.06;
    const drawY = shoulderY - collarLift;
    ctx.save();
    ctx.translate(cx, drawY);
    if (hasBody && Math.abs(angle) > 0.01) ctx.rotate(angle);
    ctx.globalAlpha = 0.90;
    ctx.drawImage(img, -garmentW / 2, 0, garmentW, garmentH);
    ctx.restore();
  }
}
