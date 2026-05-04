/** 🛡️ MOTOR DE GESTOS V11.0 - "MINORITY REPORT"
 * PATENTE: PCT/EP2025/067317
 * Optimizado para: Rendimiento 60fps & Cero Falsos Positivos
 */

const GESTURE_CONFIG = {
  SNAP_THRESHOLD: 0.05, // Umbral de cercanía en 3D
  STABILITY_FRAMES: 3,   // Cuántos frames debe durar el contacto
  COOLDOWN_MS: 2000      // Evitar compras dobles
};

let snapFrameCount = 0;
let lastTriggerTime = 0;

export const detectSovereignSnap = (handLandmarks) => {
  if (!handLandmarks) return false;

  const now = Date.now();
  if (now - lastTriggerTime < GESTURE_CONFIG.COOLDOWN_MS) return false;

  const thumb = handLandmarks[4];   // Pulgar
  const middle = handLandmarks[12]; // Corazón

  // 1. Cálculo en Espacio 3D (Z Incluido) - Recomendación Auditoría 1
  const dist = Math.hypot(
    thumb.x - middle.x,
    thumb.y - middle.y,
    (thumb.z || 0) - (middle.z || 0)
  );

  // 2. Filtro de Estabilidad - Recomendación Auditoría 2
  if (dist < GESTURE_CONFIG.SNAP_THRESHOLD) {
    snapFrameCount++;
    if (snapFrameCount >= GESTURE_CONFIG.STABILITY_FRAMES) {
      snapFrameCount = 0;
      lastTriggerTime = now;
      return true;
    }
  } else {
    snapFrameCount = 0;
  }

  return false;
};

export default {
  detectSovereignSnap,
  GESTURE_CONFIG,
};
