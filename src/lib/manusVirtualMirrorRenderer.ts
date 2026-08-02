/**
 * Drop-in renderer for Manus VirtualMirror (Overnight /mirror route).
 * Replace functions renderGarmentOnBody ($3), add smoothLandmarks, upgrade model to heavy.
 *
 * Copy this file into Manus client/src/lib/ and import from VirtualMirror page.
 */

export type PoseLandmark = {
  x: number;
  y: number;
  z?: number;
  visibility?: number;
};

export type GarmentRenderConfig = {
  shoulderWidthRatio: number;
  neckY: number;
  compositeMode?: GlobalCompositeOperation;
  opacity?: number;
};

const MIN_VISIBILITY = 0.35;
const LS = 11;
const RS = 12;
const LH = 23;
const RH = 24;
const NOSE = 0;

function clamp(n: number, min: number, max: number) {
  return Math.max(min, Math.min(max, n));
}

function vis(lm: PoseLandmark | undefined) {
  return lm?.visibility ?? 0;
}

export function smoothLandmarks(
  current: PoseLandmark[],
  previous: PoseLandmark[] | null,
  alpha = 0.38,
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
  glow: { color: string; blur: number; alpha: number } | null = null,
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

  const lsX = leftShoulder.x * canvasW;
  const lsY = leftShoulder.y * canvasH;
  const rsX = rightShoulder.x * canvasW;
  const rsY = rightShoulder.y * canvasH;

  const shoulderDist = Math.hypot(rsX - lsX, rsY - lsY);
  if (shoulderDist < 8) return false;

  const centerX = (lsX + rsX) / 2;
  const centerY = (lsY + rsY) / 2;
  const angle = Math.atan2(rsY - lsY, rsX - lsX);
  const neckY = clamp(garment.neckY ?? 0.18, 0.08, 0.45);
  const shoulderRatio = Math.max(garment.shoulderWidthRatio, 0.28);

  let scale = shoulderDist / (img.naturalWidth * shoulderRatio);

  const leftHip = landmarks[LH];
  const rightHip = landmarks[RH];
  if (leftHip && rightHip && vis(leftHip) >= MIN_VISIBILITY && vis(rightHip) >= MIN_VISIBILITY) {
    const hipMidY = ((leftHip.y + rightHip.y) / 2) * canvasH;
    const torsoPx = Math.max(hipMidY - centerY, shoulderDist * 0.8);
    const garmentTorsoPx = img.naturalHeight * (1 - neckY) * scale;
    if (garmentTorsoPx > 1) {
      scale *= clamp(torsoPx / garmentTorsoPx, 0.82, 1.18);
    }
  }

  const nose = landmarks[NOSE];
  let anchorX = centerX;
  let anchorY = centerY;
  if (nose && vis(nose) >= MIN_VISIBILITY) {
    anchorX = centerX * 0.9 + nose.x * canvasW * 0.1;
    anchorY = centerY * 0.88 + nose.y * canvasH * 0.12;
  }

  const drawW = img.naturalWidth * scale;
  const drawH = img.naturalHeight * scale;
  const offsetX = -drawW / 2;
  const offsetY = -(drawH * neckY);

  ctx.save();
  ctx.translate(anchorX, anchorY);
  ctx.rotate(angle);

  if (glow && glow.alpha > 0) {
    ctx.globalCompositeOperation = "source-over";
    ctx.globalAlpha = glow.alpha;
    ctx.shadowColor = glow.color;
    ctx.shadowBlur = glow.blur;
    ctx.drawImage(img, offsetX, offsetY, drawW, drawH);
    ctx.shadowColor = "transparent";
    ctx.shadowBlur = 0;
  }

  ctx.globalCompositeOperation = garment.compositeMode ?? "source-over";
  ctx.globalAlpha = garment.opacity ?? 0.92;
  ctx.drawImage(img, offsetX, offsetY, drawW, drawH);
  ctx.restore();
  return true;
}

/** Pose model — use HEAVY not lite for shoulder accuracy */
export const POSE_MODEL_HEAVY =
  "https://storage.googleapis.com/mediapipe-models/pose_landmarker/pose_landmarker_heavy/float16/latest/pose_landmarker_heavy.task";

/** Tuned neckY / shoulderWidthRatio for Elena CDN garments */
export const ELENA_GARMENT_TUNING: Record<number, { shoulderWidthRatio: number; neckY: number }> = {
  1: { shoulderWidthRatio: 0.38, neckY: 0.16 },
  2: { shoulderWidthRatio: 0.4, neckY: 0.14 },
  3: { shoulderWidthRatio: 0.36, neckY: 0.17 },
  4: { shoulderWidthRatio: 0.42, neckY: 0.11 },
  5: { shoulderWidthRatio: 0.39, neckY: 0.15 },
};
