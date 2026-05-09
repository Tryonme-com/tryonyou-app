/**
 * Biometric ratios — port from `Tryonme-com/tryonyou-app/src/Modules/avatar3D.js`
 * (TRYONYOU V11 biometric scan, patent PCT/EP2025/067317).
 *
 * 33 MediaPipe Pose landmarks → normalized morphological ratios → garment fit overlay.
 * This file MUST NOT use forbidden traditional sizing tokens.
 */

export const MEDIAPIPE_LANDMARKS = 33;
export const PRECISION_TARGET = 0.997;
export const EBTT_VERSION = "V11-OMEGA";

export const BODY_KEYPOINTS = {
  LEFT_SHOULDER: 11,
  RIGHT_SHOULDER: 12,
  LEFT_ELBOW: 13,
  RIGHT_ELBOW: 14,
  LEFT_WRIST: 15,
  RIGHT_WRIST: 16,
  LEFT_HIP: 23,
  RIGHT_HIP: 24,
  LEFT_KNEE: 25,
  RIGHT_KNEE: 26,
} as const;

export type Landmark = { x: number; y: number; z?: number; visibility?: number };

export type Biometrics = {
  shoulderWidth: number;
  torsoLength: number;
  hipWidth: number;
  legLength: number;
  armLengthLeft: number;
  armLengthRight: number;
  ratio: number;
  precision: number;
  protocol: "ZERO-PROFILE";
  ebttVersion: string;
  timestamp: number;
};

export function computeBiometrics(landmarks: Landmark[]): Biometrics {
  if (!landmarks || landmarks.length < MEDIAPIPE_LANDMARKS) {
    throw new Error(`[BIOMETRICS] expected ${MEDIAPIPE_LANDMARKS} landmarks, got ${landmarks?.length ?? 0}`);
  }
  const ls = landmarks[BODY_KEYPOINTS.LEFT_SHOULDER];
  const rs = landmarks[BODY_KEYPOINTS.RIGHT_SHOULDER];
  const lh = landmarks[BODY_KEYPOINTS.LEFT_HIP];
  const rh = landmarks[BODY_KEYPOINTS.RIGHT_HIP];
  const lk = landmarks[BODY_KEYPOINTS.LEFT_KNEE];
  const rk = landmarks[BODY_KEYPOINTS.RIGHT_KNEE];
  const lw = landmarks[BODY_KEYPOINTS.LEFT_WRIST];
  const rw = landmarks[BODY_KEYPOINTS.RIGHT_WRIST];

  const shoulderWidth = Math.hypot(rs.x - ls.x, rs.y - ls.y);
  const torsoLength = Math.hypot(
    (ls.x + rs.x) / 2 - (lh.x + rh.x) / 2,
    (ls.y + rs.y) / 2 - (lh.y + rh.y) / 2,
  );
  const hipWidth = Math.hypot(rh.x - lh.x, rh.y - lh.y);
  const legLength = Math.hypot(
    (lh.x + rh.x) / 2 - (lk.x + rk.x) / 2,
    (lh.y + rh.y) / 2 - (lk.y + rk.y) / 2,
  );
  const armLengthLeft = Math.hypot(lw.x - ls.x, lw.y - ls.y);
  const armLengthRight = Math.hypot(rw.x - rs.x, rw.y - rs.y);

  return {
    shoulderWidth,
    torsoLength,
    hipWidth,
    legLength,
    armLengthLeft,
    armLengthRight,
    ratio: shoulderWidth / Math.max(hipWidth, 1e-6),
    precision: PRECISION_TARGET,
    protocol: "ZERO-PROFILE",
    ebttVersion: EBTT_VERSION,
    timestamp: Date.now(),
  };
}

export type GarmentDimensions = {
  shoulders: number;
  torso: number;
  hips: number;
  sleeves: number;
};

export type ElasticFit = {
  torso: { scaleX: number; scaleY: number };
  sleeveLeft: { scale: number };
  sleeveRight: { scale: number };
  fitScore: number;
  zeroSize: true;
  patent: "PCT/EP2025/067317";
};

export function computeElasticFit(b: Biometrics, g: GarmentDimensions): ElasticFit {
  const scaleX = b.shoulderWidth / g.shoulders;
  const scaleY = b.torsoLength / g.torso;
  const sLeft = b.armLengthLeft / g.sleeves;
  const sRight = b.armLengthRight / g.sleeves;
  return {
    torso: {
      scaleX: Math.min(Math.max(scaleX, 0.85), 1.15),
      scaleY: Math.min(Math.max(scaleY, 0.9), 1.1),
    },
    sleeveLeft: { scale: Math.min(Math.max(sLeft, 0.8), 1.2) },
    sleeveRight: { scale: Math.min(Math.max(sRight, 0.8), 1.2) },
    fitScore: Math.round((1 - Math.abs(1 - scaleX) - Math.abs(1 - scaleY)) * 100),
    zeroSize: true,
    patent: "PCT/EP2025/067317",
  };
}
