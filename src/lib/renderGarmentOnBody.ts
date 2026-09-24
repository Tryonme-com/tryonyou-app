export interface PoseLandmark {
  x: number;
  y: number;
  z?: number;
  visibility?: number;
  [key: string]: any;
}

export interface GarmentRenderConfig {
  scaleFactor?: number;
  verticalOffset?: number;
  shoulderWidthRatio?: number;
  neckY?: number;
  opacity?: number;
  [key: string]: any;
}

export interface GlowOptions {
  enabled?: boolean;
  color?: string;
  intensity?: number;
  blur?: number;
  alpha?: number;
  [key: string]: any;
}

export function smoothLandmarks(current: any, previous: any, alpha: number = 0.5): any {
  if (!current) return previous || [];
  if (!previous || previous.length === 0) return current || [];
  return current.map((pt: any, i: number) => {
    const prev = previous[i];
    if (!prev) return pt;
    return {
      x: prev.x * (1 - alpha) + pt.x * alpha,
      y: prev.y * (1 - alpha) + pt.y * alpha,
      z: prev.z !== undefined && pt.z !== undefined ? prev.z * (1 - alpha) + pt.z * alpha : pt.z,
      visibility: pt.visibility
    };
  });
}

export function renderGarmentOnBody(
  ctx: CanvasRenderingContext2D,
  image: HTMLImageElement,
  landmarks: any,
  arg4?: any,
  arg5?: any,
  arg6?: any,
  arg7?: any
): boolean {
  if (!landmarks || landmarks.length < 13) return false;

  const leftShoulder = landmarks[11];
  const rightShoulder = landmarks[12];
  const nose = landmarks[0];

  if (!leftShoulder || !rightShoulder) return false;

  let canvasWidth = 1000;
  let canvasHeight = 1000;
  let config: GarmentRenderConfig = {};
  let glow: GlowOptions = {};

  const dynamicArgs = [arg4, arg5, arg6, arg7];
  let numCount = 0;
  for (const val of dynamicArgs) {
    if (typeof val === 'number') {
      if (numCount === 0) canvasWidth = val;
      else canvasHeight = val;
      numCount++;
    } else if (typeof val === 'object' && val !== null) {
      if ('blur' in val || 'intensity' in val || 'enabled' in val || 'alpha' in val) {
        glow = val;
      } else {
        config = val;
      }
    }
  }

  const lX = leftShoulder.x * canvasWidth;
  const lY = leftShoulder.y * canvasHeight;
  const rX = rightShoulder.x * canvasWidth;
  const rY = rightShoulder.y * canvasHeight;

  const shoulderCenterX = (lX + rX) / 2;
  const shoulderCenterY = (lY + rY) / 2;
  const shoulderWidth = Math.hypot(rX - lX, rY - lY);

  const angle = Math.atan2(rY - lY, rX - lX);

  const baseScaleFactor = config.scaleFactor ?? (config.shoulderWidthRatio ? config.shoulderWidthRatio * 6 : 2.2);
  const garmentWidth = shoulderWidth * baseScaleFactor;
  const aspect = image.height && image.width ? image.height / image.width : 1.25;
  const garmentHeight = garmentWidth * aspect;

  const verticalOffset = config.verticalOffset !== undefined
    ? config.verticalOffset
    : (config.neckY !== undefined 
        ? shoulderCenterY - (config.neckY * canvasHeight)
        : (nose ? (shoulderCenterY - (nose.y * canvasHeight)) * 0.45 : garmentHeight * 0.12));

  const renderX = shoulderCenterX;
  const renderY = shoulderCenterY - verticalOffset;

  ctx.save();
  ctx.translate(renderX, renderY);
  ctx.rotate(angle);

  ctx.globalAlpha = config.opacity ?? 1.0;
  ctx.globalCompositeOperation = 'source-over';

  if (glow?.enabled) {
    ctx.shadowColor = glow.color || '#C5A46D';
    ctx.shadowBlur = glow.blur ?? glow.intensity ?? 15;
  }

  ctx.drawImage(
    image,
    -garmentWidth / 2,
    -garmentHeight * 0.28,
    garmentWidth,
    garmentHeight
  );

  ctx.restore();
  return true;
}
