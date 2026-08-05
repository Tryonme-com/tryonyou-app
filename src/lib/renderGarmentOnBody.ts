/**
 * TRYONYOU Robert Engine — Biometric Garment Real-Time Alignment & Depth-Scaling Renderer
 * Patent PCT/EP2025/067317 — Zero-Size UX Protocol
 */

export interface PoseLandmark {
  x: number;
  y: number;
  z?: number;
  visibility?: number;
}

export function renderGarmentWithRobertEngine(
  ctx: CanvasRenderingContext2D,
  image: HTMLImageElement,
  landmarks: PoseLandmark[],
  canvasWidth: number,
  canvasHeight: number
) {
  if (!landmarks || landmarks.length < 13) return;

  const leftShoulder = landmarks[11];
  const rightShoulder = landmarks[12];
  const nose = landmarks[0];

  if (!leftShoulder || !rightShoulder) return;

  const lX = leftShoulder.x * canvasWidth;
  const lY = leftShoulder.y * canvasHeight;
  const rX = rightShoulder.x * canvasWidth;
  const rY = rightShoulder.y * canvasHeight;

  const shoulderCenterX = (lX + rX) / 2;
  const shoulderCenterY = (lY + rY) / 2;
  const shoulderWidth = Math.hypot(rX - lX, rY - lY);

  const angle = Math.atan2(rY - lY, rX - lX);

  const baseScaleFactor = 2.2;
  const garmentWidth = shoulderWidth * baseScaleFactor;
  const aspect = image.height / image.width;
  const garmentHeight = garmentWidth * aspect;

  const verticalOffset = nose
    ? (shoulderCenterY - (nose.y * canvasHeight)) * 0.45
    : garmentHeight * 0.12;

  const renderX = shoulderCenterX;
  const renderY = shoulderCenterY - verticalOffset;

  ctx.save();
  ctx.translate(renderX, renderY);
  ctx.rotate(angle);

  ctx.drawImage(
    image,
    -garmentWidth / 2,
    -garmentHeight * 0.28,
    garmentWidth,
    garmentHeight
  );

  ctx.restore();
}
