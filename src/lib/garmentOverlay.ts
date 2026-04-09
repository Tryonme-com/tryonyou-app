type OverlayAnchorPoint = { x: number; y: number };

export type OverlayProjection = {
  x: number;
  y: number;
  width: number;
  height: number;
  angleRad: number;
};

export type RuntimeGarmentOverlay = {
  garmentId: string;
  brandLine: string;
  color: string;
  alpha: number;
  lastUpdatedAt: number;
};

export type GarmentOverlayState = {
  overlay: RuntimeGarmentOverlay | null;
  color: string;
  lastUpdatedAt: number;
};

type NormalizedLandmark = {
  x: number;
  y: number;
  visibility?: number;
};

function pickLandmark(landmarks: NormalizedLandmark[], idx: number): NormalizedLandmark | null {
  const p = landmarks[idx];
  if (!p) return null;
  if (p.visibility !== undefined && p.visibility < 0.35) return null;
  return p;
}

export function computeShoulderProjection(
  landmarks: NormalizedLandmark[],
  frameWidth: number,
  frameHeight: number,
): OverlayProjection | null {
  const left = pickLandmark(landmarks, 11);
  const right = pickLandmark(landmarks, 12);
  const leftHip = pickLandmark(landmarks, 23);
  const rightHip = pickLandmark(landmarks, 24);
  if (!left || !right || !leftHip || !rightHip) return null;

  const l: OverlayAnchorPoint = { x: left.x * frameWidth, y: left.y * frameHeight };
  const r: OverlayAnchorPoint = { x: right.x * frameWidth, y: right.y * frameHeight };
  const lh: OverlayAnchorPoint = { x: leftHip.x * frameWidth, y: leftHip.y * frameHeight };
  const rh: OverlayAnchorPoint = { x: rightHip.x * frameWidth, y: rightHip.y * frameHeight };

  const shoulderDx = r.x - l.x;
  const shoulderDy = r.y - l.y;
  const shoulderWidth = Math.max(20, Math.hypot(shoulderDx, shoulderDy));

  const hipCenterY = (lh.y + rh.y) / 2;
  const shoulderCenterY = (l.y + r.y) / 2;
  const torsoHeight = Math.max(40, hipCenterY - shoulderCenterY);

  const centerX = (l.x + r.x) / 2;
  const centerY = shoulderCenterY + torsoHeight * 0.5;

  return {
    x: centerX,
    y: centerY,
    width: shoulderWidth * 1.55,
    height: torsoHeight * 1.3,
    angleRad: Math.atan2(shoulderDy, shoulderDx),
  };
}

function hashHue(input: string): number {
  let hash = 0;
  for (let i = 0; i < input.length; i++) {
    hash = (hash * 31 + input.charCodeAt(i)) >>> 0;
  }
  return hash % 360;
}

export function drawGarmentOverlay(
  ctx: CanvasRenderingContext2D,
  projection: OverlayProjection,
  garmentId: string,
  brandLine: string,
): void {
  const hue = hashHue(`${brandLine}:${garmentId}`);
  const fillA = `hsla(${hue}, 78%, 46%, 0.30)`;
  const fillB = `hsla(${(hue + 38) % 360}, 72%, 58%, 0.24)`;
  const stroke = `hsla(${(hue + 20) % 360}, 92%, 66%, 0.9)`;

  ctx.save();
  ctx.translate(projection.x, projection.y);
  ctx.rotate(projection.angleRad);
  ctx.beginPath();
  ctx.roundRect(
    -projection.width / 2,
    -projection.height / 2,
    projection.width,
    projection.height,
    Math.min(24, projection.width * 0.08),
  );
  const grad = ctx.createLinearGradient(0, -projection.height / 2, 0, projection.height / 2);
  grad.addColorStop(0, fillA);
  grad.addColorStop(1, fillB);
  ctx.fillStyle = grad;
  ctx.fill();
  ctx.lineWidth = 2;
  ctx.strokeStyle = stroke;
  ctx.stroke();
  ctx.restore();

  const labelY = Math.max(28, projection.y - projection.height / 2 - 10);
  ctx.save();
  ctx.font = "600 12px Inter, system-ui, sans-serif";
  ctx.textAlign = "center";
  ctx.fillStyle = "rgba(10,10,10,0.78)";
  const text = `${brandLine} · ${garmentId}`;
  const padX = 10;
  const w = ctx.measureText(text).width + padX * 2;
  const h = 20;
  ctx.fillRect(projection.x - w / 2, labelY - h + 3, w, h);
  ctx.strokeStyle = stroke;
  ctx.lineWidth = 1;
  ctx.strokeRect(projection.x - w / 2, labelY - h + 3, w, h);
  ctx.fillStyle = "#f5f1e8";
  ctx.fillText(text, projection.x, labelY - 3);
  ctx.restore();
}

export function createGarmentOverlayState(): GarmentOverlayState {
  return {
    overlay: null,
    color: "#d4af37",
    lastUpdatedAt: 0,
  };
}

export function resolveOverlayColor(input: unknown): string {
  const s = String(input ?? "").trim();
  if (/^#[0-9a-fA-F]{6}$/.test(s) || /^#[0-9a-fA-F]{3}$/.test(s)) {
    return s;
  }
  return "#d4af37";
}
