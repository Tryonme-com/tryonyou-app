/** 🛡️ CONFIGURACIÓN SOBERANA DEL MOTOR */
const engineConfig = {
  mode: import.meta.env.VITE_ENGINE_MODE || 'STANDARD',
  precision: parseFloat(import.meta.env.VITE_PRECISION_LEVEL || '0.5'),
  overlay: import.meta.env.VITE_OVERLAY_SYNC?.toUpperCase() === 'TRUE'
};

console.log(`🔱 MOTOR INICIALIZADO EN MODO: ${engineConfig.mode}`);

/** 🛡️ ROBERT ENGINE V10.5 - INTEGRACIÓN MANUS */

// Normalised-landmark distance threshold for snap gesture (thumb tip → middle-finger tip)
const SNAP_DISTANCE_THRESHOLD = 0.03;

export const syncExtremities = (landmarks) => {
  const { leftHand, rightHand, pose } = landmarks;

  // Anclaje al suelo (Pies 31, 32)
  const leftFoot = pose?.[31];
  const rightFoot = pose?.[32];
  const groundY = Math.max(leftFoot?.y ?? 0, rightFoot?.y ?? 0);

  // Detección del Chasquido (Pulgar + Corazón)
  if (rightHand) {
    const thumbTip = rightHand[4];
    const middleTip = rightHand[12];
    if (thumbTip && middleTip) {
      const dist = Math.hypot(thumbTip.x - middleTip.x, thumbTip.y - middleTip.y);
      if (dist < SNAP_DISTANCE_THRESHOLD) return "TRIGGER_SNAP";
    }
  }
  return groundY;
};

export default engineConfig;

/** 🛡️ ROBERT ENGINE V10.5 - INTEGRACIÓN MANUS */
export const syncExtremities = (landmarks) => {
  const { leftHand, rightHand, pose } = landmarks;

  // Anclaje al suelo (Pies 31, 32)
  const groundY = Math.max(pose[31].y, pose[32].y);

  // Detección del Chasquido (Pulgar + Corazón)
  if (rightHand) {
    const dist = Math.hypot(rightHand[4].x - rightHand[12].x, rightHand[4].y - rightHand[12].y);
    if (dist < 0.03) return "TRIGGER_SNAP";
  }
  return groundY;
};
