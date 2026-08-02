/**
 * Real-Time Garment Overlay Renderer — Canvas 2D + MediaPipe Pose Landmarks.
 *
 * Anchors garment PNGs to shoulders (11/12) with optional hip/torso scaling,
 * nose-assisted collar alignment, and EMA smoothing for live movement.
 *
 * Patent PCT/EP2025/067317 — TRYONYOU Zero-Size Protocol
 */

export interface PoseLandmark {
  x: number;
  y: number;
  z?: number;
  visibility?: number;
}

export interface GarmentRenderConfig {
  /** Shoulder span as fraction of garment image width (0..1). */
  shoulderWidthRatio: number;
  /** Y fraction in garment PNG where shoulder line sits (0=top, 1=bottom). */
  neckY: number;
  compositeMode?: GlobalCompositeOperation;
  opacity?: number;
}

export interface GlowOptions {
  color: string;
  blur: number;
  alpha: number;
}

const MIN_VISIBILITY = 0.35;
const DEFAULT_OPACITY = 0.92;
const DEFAULT_COMPOSITE: GlobalCompositeOperation = "source-over";
const SMOOTH_ALPHA = 0.38;

const LS = 11;
const RS = 12;
const LH = 23;
const RH = 24;
const NOSE = 0;

function clamp(n: number, min: number, max: number): number {
  return Math.max(min, Math.min(max, n));
}

function vis(lm: PoseLandmark | undefined): number {
  return lm?.visibility ?? 0;
}

function toPx(lm: PoseLandmark, canvasW: number, canvasH: number): { x: number; y: number } {
  return { x: lm.x * canvasW, y: lm.y * canvasH };
}

/** EMA smoothing — keeps overlay glued to body without jitter. */
export function smoothLandmarks(
  current: PoseLandmark[],
  previous: PoseLandmark[] | null,
  alpha = SMOOTH_ALPHA,
): PoseLandmark[] {
  if (!previous || previous.length !== current.length) return current;
  return current.map((lm, i) => {
    const prev = previous[i];
    if (vis(lm) < MIN_VISIBILITY || vis(prev) < MIN_VISIBILITY) return lm;
    return {
      ...lm,
      x: prev.x + alpha * (lm.x - prev.x),
      y: prev.y + alpha * (lm.y - prev.y),
    };
  });
}

export function renderGarmentOnBody(
  ctx: CanvasRenderingContext2D,
  img: HTMLImageElement,
  landmarks: PoseLandmark[],
  garment: GarmentRenderConfig,
  canvasW: number,
  canvasH: number,
  glow: GlowOptions | null = null,
): boolean {
  const leftShoulder = landmarks[LS];
  const rightShoulder = landmarks[RS];

  if (
    !leftShoulder ||
    !rightShoulder ||
    vis(leftShoulder) < MIN_VISIBILITY ||
    vis(rightShoulder) < MIN_VISIBILITY
  ) {
    return false;
  }

  const ls = toPx(leftShoulder, canvasW, canvasH);
  const rs = toPx(rightShoulder, canvasW, canvasH);

  const shoulderDist = Math.hypot(rs.x - ls.x, rs.y - ls.y);
  if (shoulderDist < 8) return false;

  const centerX = (ls.x + rs.x) / 2;
  const centerY = (ls.y + rs.y) / 2;
  const angle = Math.atan2(rs.y - ls.y, rs.x - ls.x);

  const neckY = clamp(garment.neckY ?? 0.18, 0.08, 0.45);
  const shoulderRatio = Math.max(garment.shoulderWidthRatio, 0.28);

  let scale = shoulderDist / (img.naturalWidth * shoulderRatio);

  const leftHip = landmarks[LH];
  const rightHip = landmarks[RH];
  if (
    leftHip &&
    rightHip &&
    vis(leftHip) >= MIN_VISIBILITY &&
    vis(rightHip) >= MIN_VISIBILITY
  ) {
    const hipMidY = ((leftHip.y + rightHip.y) / 2) * canvasH;
    const torsoPx = Math.max(hipMidY - centerY, shoulderDist * 0.8);
    const garmentTorsoPx = img.naturalHeight * (1 - neckY) * scale;
    if (garmentTorsoPx > 1) {
      const torsoScale = torsoPx / garmentTorsoPx;
      scale *= clamp(torsoScale, 0.82, 1.18);
    }
  }

  const nose = landmarks[NOSE];
  let anchorX = centerX;
  let anchorY = centerY;
  if (nose && vis(nose) >= MIN_VISIBILITY) {
    const nosePx = toPx(nose, canvasW, canvasH);
    anchorX = centerX * 0.9 + nosePx.x * 0.1;
    anchorY = centerY * 0.88 + nosePx.y * 0.12;
  }

  const drawW = img.naturalWidth * scale;
  const drawH = img.naturalHeight * scale;
  const offsetX = -drawW / 2;
  const offsetY = -(drawH * neckY);

  const drawPass = (alpha: number, composite: GlobalCompositeOperation, shadow: GlowOptions | null) => {
    ctx.globalCompositeOperation = composite;
    ctx.globalAlpha = alpha;
    if (shadow && shadow.alpha > 0) {
      ctx.shadowColor = shadow.color;
      ctx.shadowBlur = shadow.blur;
    }
    ctx.drawImage(img, offsetX, offsetY, drawW, drawH);
    ctx.shadowColor = "transparent";
    ctx.shadowBlur = 0;
  };

  ctx.save();
  ctx.translate(anchorX, anchorY);
  ctx.rotate(angle);

  if (glow && glow.alpha > 0) {
    drawPass(glow.alpha, "source-over", glow);
  }

  drawPass(garment.opacity ?? DEFAULT_OPACITY, garment.compositeMode ?? DEFAULT_COMPOSITE, null);
  ctx.restore();

  return true;
}

export function adaptLegacyOverlay(
  scaleFactor: number,
  offsetY: number,
  imageNaturalH: number,
  shoulderRatioHint = 0.45,
): GarmentRenderConfig {
  return {
    shoulderWidthRatio: shoulderRatioHint / scaleFactor,
    neckY: clamp((imageNaturalH * 0.16 + offsetY) / imageNaturalH, 0.1, 0.35),
    compositeMode: "source-over",
    opacity: 0.92,
  };
}
