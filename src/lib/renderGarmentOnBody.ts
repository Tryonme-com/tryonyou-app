/**
 * Real-Time Garment Overlay Renderer — Canvas 2D + MediaPipe Pose Landmarks.
 *
 * Renders a garment PNG over the user's body using shoulder landmarks (11, 12)
 * for dynamic scaling, rotation, and positioning. Uses "multiply" composite
 * for fabric realism on light/medium backgrounds with automatic fallback.
 *
 * Patent PCT/EP2025/067317 — TRYONYOU–ABVETOS–ULTRA–PLUS–ULTIMATUM
 * Protocol: Divineo V11 — Zero-Size Sovereign Fit
 */

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

/** Normalized landmark from MediaPipe Pose (0..1 range). */
export interface PoseLandmark {
  x: number;
  y: number;
  z?: number;
  visibility?: number;
}

/** Garment metadata required for overlay rendering. */
export interface GarmentRenderConfig {
  /** Ratio of shoulder width relative to the garment image's naturalWidth (0..1). */
  shoulderWidthRatio: number;
  /** Vertical offset ratio for neck anchor point (0..1, from top of image). */
  neckY: number;
  /** Optional: composite mode override (defaults to "multiply"). */
  compositeMode?: GlobalCompositeOperation;
  /** Optional: base opacity (defaults to 0.95). */
  opacity?: number;
}

/** Options for the glow effect around the garment. */
export interface GlowOptions {
  color: string;
  blur: number;
  alpha: number;
}

// ---------------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------------

const MIN_VISIBILITY = 0.3;
const DEFAULT_SCALE_BOOST = 1.0;
const DEFAULT_OPACITY = 0.95;
const DEFAULT_COMPOSITE: GlobalCompositeOperation = "multiply";

// ---------------------------------------------------------------------------
// Main Renderer
// ---------------------------------------------------------------------------

/**
 * Renders a garment image overlay on the Canvas, anchored to the user's
 * shoulder landmarks detected by MediaPipe Pose.
 *
 * @param ctx        - Canvas 2D rendering context.
 * @param img        - Pre-loaded garment image (PNG with transparency).
 * @param landmarks  - Array of 33 MediaPipe Pose landmarks (normalized 0..1).
 * @param garment    - Garment configuration for scaling and positioning.
 * @param canvasW    - Canvas width in pixels.
 * @param canvasH    - Canvas height in pixels.
 * @param glow       - Optional glow effect parameters (null to disable).
 * @returns          - `true` if the garment was rendered, `false` if landmarks
 *                     were insufficient (low visibility or missing).
 */
export function renderGarmentOnBody(
  ctx: CanvasRenderingContext2D,
  img: HTMLImageElement,
  landmarks: PoseLandmark[],
  garment: GarmentRenderConfig,
  canvasW: number,
  canvasH: number,
  glow: GlowOptions | null = null,
): boolean {
  // 1. Extract shoulder landmarks (MediaPipe Pose indices 11 & 12)
  const leftShoulder = landmarks[11];
  const rightShoulder = landmarks[12];

  if (
    !leftShoulder ||
    !rightShoulder ||
    (leftShoulder.visibility ?? 0) < MIN_VISIBILITY ||
    (rightShoulder.visibility ?? 0) < MIN_VISIBILITY
  ) {
    return false;
  }

  // 2. Convert normalized coords to canvas pixels (mirrored X for webcam)
  const lsX = leftShoulder.x * canvasW;
  const lsY = leftShoulder.y * canvasH;
  const rsX = rightShoulder.x * canvasW;
  const rsY = rightShoulder.y * canvasH;

  // 3. Compute dynamic metrics
  const shoulderDist = Math.hypot(rsX - lsX, rsY - lsY);
  const scale =
    (shoulderDist / (img.naturalWidth * garment.shoulderWidthRatio)) *
    DEFAULT_SCALE_BOOST;

  // 4. Compute transform origin and rotation angle
  const centerX = (lsX + rsX) / 2;
  const centerY = (lsY + rsY) / 2;
  const angle = Math.atan2(rsY - lsY, rsX - lsX);

  // 5. Compute draw dimensions
  let drawW = img.naturalWidth * scale;
  let drawH = img.naturalHeight * scale;
  if (drawW < shoulderDist * 1.5) {
    drawW = shoulderDist * 2.2;
    drawH = drawW * (img.naturalHeight / img.naturalWidth);
  }

  ctx.save();
  ctx.translate(centerX, centerY);
  ctx.rotate(angle);

  // 6. Apply glow effect if requested
  if (glow && glow.alpha > 0) {
    ctx.shadowColor = glow.color;
    ctx.shadowBlur = glow.blur;
    ctx.globalAlpha = glow.alpha;
    ctx.drawImage(img, -drawW / 2, -(drawH * (garment.neckY || 0.25)), drawW, drawH);
    // Reset shadow for main draw
    ctx.shadowColor = "transparent";
    ctx.shadowBlur = 0;
  }

  // 7. Main garment draw with fabric-realistic composite
  ctx.globalCompositeOperation = garment.compositeMode ?? DEFAULT_COMPOSITE;
  ctx.globalAlpha = garment.opacity ?? DEFAULT_OPACITY;
  ctx.drawImage(img, -drawW / 2, -(drawH * (garment.neckY || 0.25)), drawW, drawH);

  ctx.restore();

  return true;
}

// ---------------------------------------------------------------------------
// Adapter: GarmentOverlayConfig → GarmentRenderConfig
// ---------------------------------------------------------------------------

/**
 * Converts the legacy GarmentOverlayConfig (from garmentOverlays.ts) into
 * the GarmentRenderConfig expected by the renderer.
 *
 * @param scaleFactor       - Legacy scale factor (e.g. 1.15).
 * @param offsetY           - Legacy vertical offset in pixels.
 * @param imageNaturalH     - The garment image's naturalHeight.
 * @param shoulderRatioHint - Estimated shoulder-to-image-width ratio (default 0.45).
 */
export function adaptLegacyOverlay(
  scaleFactor: number,
  offsetY: number,
  imageNaturalH: number,
  shoulderRatioHint = 0.45,
): GarmentRenderConfig {
  return {
    shoulderWidthRatio: shoulderRatioHint / scaleFactor,
    neckY: Math.max(0, Math.min(1, (imageNaturalH / 2 + offsetY) / imageNaturalH)),
    compositeMode: "multiply",
    opacity: 0.95,
  };
}
