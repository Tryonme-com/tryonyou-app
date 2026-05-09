/**
 * TRYONYOU — Overlay Renderer.
 *
 * Inspired by the original tryonyou.org renderer (drape coefficient, weight GSM,
 * elasticity-based pulse, golden specular highlight). Adapted to use
 * the per-garment fabric record from `catalog.ts`.
 */

import type { Fabric, Garment } from "@/lib/catalog";
import { FABRICS } from "@/lib/catalog";

export type AnchorState = {
  cx: number;
  shoulderY: number;
  hipY: number;
  shoulderW: number;
  angle: number;
  hasBody: boolean;
};

export function getFabric(g: Garment): Fabric | undefined {
  return FABRICS[g.fabricKey];
}

function silhouetteScale(f: Fabric): number {
  // higher drape coefficient → tighter, lower → wider flare
  return 2.2 + (0.5 - f.drapeCoefficient * 0.4);
}

function lengthScale(f: Fabric, base: number): number {
  const t = Math.min(1, Math.max(0, (f.weightGSM - 50) / 350));
  return base * (1 + t * 0.15);
}

function alphaForFitScore(score: number, f: Fabric, t: number): number {
  if (score >= 95) {
    const sparkle = f.frictionCoefficient < 0.3 ? Math.sin(t * 0.002) * 0.03 : 0;
    return Math.min(0.95, 0.88 + 0.07 + sparkle);
  }
  const wobble = Math.sin(t * 0.004) * 0.06;
  return Math.max(0.7, 0.88 + wobble);
}

function elasticityPulse(f: Fabric, t: number): number {
  const amp = (f.elasticityPct / 100) * 0.02;
  return 1 + Math.sin(t * 0.003) * amp;
}

/**
 * Draw the overlay image onto the canvas, anchored to MediaPipe-derived
 * shoulder/hip positions. Falls back to a static placement if no body.
 */
export function drawGarmentOverlay(
  ctx: CanvasRenderingContext2D,
  img: HTMLImageElement,
  anchor: AnchorState,
  garment: Garment,
  fitScore: number,
  canvasW: number,
  canvasH: number,
): void {
  const fabric = getFabric(garment);
  const t = Date.now();
  const { cx, shoulderY, hipY, shoulderW, angle, hasBody } = anchor;
  const torsoH = hipY - shoulderY;

  // Accessories use a small bag/scarf rendering near the hips.
  if (garment.type === "accessoire" || garment.type === "foulard") {
    const w = hasBody ? shoulderW * 0.85 : canvasW * 0.18;
    const ratio = img.naturalHeight / img.naturalWidth;
    const h = w * ratio;
    const sway = Math.sin(t * 0.002) * 4;
    const x = cx + (hasBody ? shoulderW * 0.55 : canvasW * 0.12) + sway;
    const y = hipY - h * 0.3;
    ctx.save();
    ctx.globalAlpha = alphaForFitScore(fitScore, fabric ?? defaultFab(), t);
    if (hasBody && Math.abs(angle) > 0.01) {
      ctx.translate(x + w / 2, y + h / 2);
      ctx.rotate(angle * 0.3);
      ctx.drawImage(img, -w / 2, -h / 2, w, h);
    } else {
      ctx.drawImage(img, x, y, w, h);
    }
    ctx.restore();
    return;
  }

  const fab = fabric ?? defaultFab();
  const widthScale = silhouetteScale(fab) * elasticityPulse(fab, t);
  const w = shoulderW * widthScale;
  const baseLen = torsoH * 1.6;
  const h = lengthScale(fab, baseLen);
  const yOffset = torsoH * 0.05;
  const y = shoulderY - yOffset;

  ctx.save();
  ctx.translate(cx, y);
  if (hasBody && Math.abs(angle) > 0.005) ctx.rotate(angle);
  if (hasBody && Math.abs(angle) > 0.03) {
    const skewX = angle * 0.15;
    ctx.transform(1, 0, skewX, 1, 0, 0);
  }
  ctx.globalCompositeOperation = "source-over";
  ctx.globalAlpha = alphaForFitScore(fitScore, fab, t);

  // Draw simply: scale the SVG silhouette to (w, h).
  ctx.drawImage(img, -w / 2, 0, w, h);

  // Specular gold gradient when fit is optimal.
  if (fitScore > 95) {
    const grad = ctx.createRadialGradient(0, h * 0.4, w * 0.1, 0, h * 0.4, w * 0.8);
    const a = 0.04 + Math.sin(t * 0.002) * 0.02;
    grad.addColorStop(0, `rgba(201, 168, 76, ${a})`);
    grad.addColorStop(1, "rgba(201, 168, 76, 0)");
    ctx.fillStyle = grad;
    ctx.fillRect(-w / 2, 0, w, h);
  }

  // Heavy fabrics → vertical drape shadows.
  if (fab.weightGSM > 150) {
    const a = Math.min(0.12, (fab.weightGSM - 150) / 1500);
    for (let i = 0; i < 3; i++) {
      const x = -w * 0.3 + i * w * 0.3;
      const segW = w * 0.15;
      const grad = ctx.createLinearGradient(x, h * 0.3, x + segW, h * 0.3);
      grad.addColorStop(0, "rgba(0, 0, 0, 0)");
      grad.addColorStop(0.5, `rgba(0, 0, 0, ${a})`);
      grad.addColorStop(1, "rgba(0, 0, 0, 0)");
      ctx.fillStyle = grad;
      ctx.fillRect(x, h * 0.2, segW, h * 0.7);
    }
  }

  // Low friction (silk, satin) → highlight glide.
  if (fab.frictionCoefficient < 0.35) {
    const x = Math.sin(t * 0.001) * w * 0.25;
    const grad = ctx.createRadialGradient(x, h * 0.35, 0, x, h * 0.35, w * 0.35);
    const a = (0.35 - fab.frictionCoefficient) * 0.2;
    grad.addColorStop(0, `rgba(255, 255, 255, ${a})`);
    grad.addColorStop(1, "rgba(255, 255, 255, 0)");
    ctx.fillStyle = grad;
    ctx.fillRect(-w / 2, 0, w, h);
  }

  // Sub-95 → diagnostic scanline.
  if (fitScore < 95 && fitScore > 0) {
    const y2 = ((t % 2000) / 2000) * h;
    ctx.strokeStyle = "rgba(201, 168, 76, 0.12)";
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.moveTo(-w / 2, y2);
    ctx.lineTo(w / 2, y2);
    ctx.stroke();
  }

  ctx.restore();
}

function defaultFab(): Fabric {
  return {
    drapeCoefficient: 0.6,
    weightGSM: 200,
    elasticityPct: 8,
    recoveryPct: 60,
    frictionCoefficient: 0.4,
    maxStrainPct: 10,
    breathability: 0.6,
    composition: "—",
  };
}
