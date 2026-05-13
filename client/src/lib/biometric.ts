/**
 * TRYONYOU — biometric.ts
 * © 2025-2026 Rubén Espinar Rodríguez — Brevet PCT/EP2025/067317
 *
 * Moteur biométrique du Protocole Zero-Size :
 *   1. Filtrage EMA (Exponential Moving Average) sur les 33 landmarks MediaPipe
 *      pour absorber le jitter de la caméra et stabiliser l'overlay vêtement.
 *   2. Correction de perspective via DeviceOrientationEvent (gyroscope) :
 *      compense l'inclinaison du téléphone pour préserver la précision
 *      des longueurs d'entrejambe et de torse.
 *   3. Layer subtraction : retire automatiquement la marge tissu apparente
 *      pour ne mesurer que le corps réel (et non corps + vêtement actuel).
 *   4. Calcul des métriques clés (épaule, torse, hanche, entrejambe) en unités
 *      relatives — JAMAIS exposées en chiffres dans l'UI : converties en
 *      barres de confiance pour respecter la philosophie Zero-Size.
 *
 * Style : silencieux, déterministe, performance-first.
 */

// ─── Types partagés ──────────────────────────────────────────────────────
export interface RawLandmark {
  x: number;        // 0-1 (relatif à la frame caméra)
  y: number;        // 0-1
  z: number;        // profondeur relative
  visibility: number; // 0-1
}

export interface FilteredLandmark {
  x: number;
  y: number;
  z: number;
  visibility: number;
}

export type LayerType = "tshirt" | "shirt" | "sweater" | "jacket" | "coat";

export interface ZeroSizeMetrics {
  shoulderWidth: number;      // unité relative (px)
  torsoLength: number;
  hipWidth: number;
  inseam: number;
  armLength: number;
  // Indicateurs de confiance 0-1 (jamais affichés en chiffres bruts)
  shoulderConfidence: number;
  torsoConfidence: number;
  hipConfidence: number;
  inseamConfidence: number;
  // Score global de qualité du verrou biométrique
  lockScore: number;
  // Layer subtraction actif ?
  layerCalibrationActive: boolean;
  // Temps de détection en ms (pour le panneau Zero-Size)
  lockTimeMs: number;
}

// ─── Indices anatomiques MediaPipe Pose ──────────────────────────────────
export const POSE_INDEX = {
  NOSE: 0,
  L_EYE_INNER: 1, L_EYE: 2, L_EYE_OUTER: 3,
  R_EYE_INNER: 4, R_EYE: 5, R_EYE_OUTER: 6,
  L_EAR: 7, R_EAR: 8,
  MOUTH_L: 9, MOUTH_R: 10,
  L_SHOULDER: 11, R_SHOULDER: 12,
  L_ELBOW: 13, R_ELBOW: 14,
  L_WRIST: 15, R_WRIST: 16,
  L_PINKY: 17, R_PINKY: 18,
  L_INDEX: 19, R_INDEX: 20,
  L_THUMB: 21, R_THUMB: 22,
  L_HIP: 23, R_HIP: 24,
  L_KNEE: 25, R_KNEE: 26,
  L_ANKLE: 27, R_ANKLE: 28,
  L_HEEL: 29, R_HEEL: 30,
  L_FOOT_INDEX: 31, R_FOOT_INDEX: 32,
} as const;

// ═══════════════════════════════════════════════════════════════════════
// 1. FILTRE EMA STABLE — supprime le jitter sans introduire de latence visible
// ═══════════════════════════════════════════════════════════════════════
export class LandmarkFilter {
  // Coefficient adaptatif : faible quand la confiance est haute (lissage doux),
  // haut quand la confiance chute (réactivité immédiate).
  private prev: FilteredLandmark[] | null = null;
  private readonly baseAlpha: number;

  constructor(baseAlpha = 0.35) {
    this.baseAlpha = baseAlpha;
  }

  reset(): void {
    this.prev = null;
  }

  apply(raw: RawLandmark[]): FilteredLandmark[] {
    if (!raw || raw.length === 0) return [];
    if (!this.prev || this.prev.length !== raw.length) {
      this.prev = raw.map((l) => ({ x: l.x, y: l.y, z: l.z, visibility: l.visibility }));
      return this.prev;
    }

    const out: FilteredLandmark[] = new Array(raw.length);
    for (let i = 0; i < raw.length; i++) {
      const r = raw[i];
      const p = this.prev[i];
      // Si visibility chute brutalement, on ré-acquiert plus vite
      const visDelta = Math.abs(r.visibility - p.visibility);
      const alpha = Math.min(0.85, this.baseAlpha + visDelta * 0.6);
      out[i] = {
        x: p.x + (r.x - p.x) * alpha,
        y: p.y + (r.y - p.y) * alpha,
        z: p.z + (r.z - p.z) * alpha,
        visibility: p.visibility + (r.visibility - p.visibility) * 0.5,
      };
    }
    this.prev = out;
    return out;
  }
}

// ═══════════════════════════════════════════════════════════════════════
// 2. CORRECTION DE PERSPECTIVE (gyroscope)
// ═══════════════════════════════════════════════════════════════════════
export class GyroCorrector {
  // Beta = inclinaison front/back (0° = vertical idéal pour photo selfie).
  // Si beta = 80° au lieu de 90°, on compense la projection Y.
  private beta = 0;
  private gamma = 0;
  private listening = false;
  private handler = (e: DeviceOrientationEvent) => {
    if (e.beta !== null) this.beta = e.beta;
    if (e.gamma !== null) this.gamma = e.gamma;
  };

  start(): void {
    if (this.listening || typeof window === "undefined") return;
    if (!("DeviceOrientationEvent" in window)) return;
    this.listening = true;
    // iOS 13+ : permission requise — silent fallback si refusée
    const Anyclass = window.DeviceOrientationEvent as any;
    if (Anyclass && typeof Anyclass.requestPermission === "function") {
      Anyclass.requestPermission().then((r: string) => {
        if (r === "granted") window.addEventListener("deviceorientation", this.handler);
      }).catch(() => { /* silencieux */ });
    } else {
      window.addEventListener("deviceorientation", this.handler);
    }
  }

  stop(): void {
    if (!this.listening) return;
    window.removeEventListener("deviceorientation", this.handler);
    this.listening = false;
  }

  /** Inclinaison verticale apparente du téléphone, en radians, par rapport à 90°. */
  getTiltCompensation(): number {
    // beta = 90° → vertical parfait → tilt = 0
    // beta = 80° → téléphone penché → tilt = 10° en radians
    const deltaDeg = 90 - this.beta;
    return (deltaDeg * Math.PI) / 180;
  }

  /**
   * Re-projette un landmark normalisé pour compenser l'inclinaison verticale.
   * Effet : étire/raccourcit l'axe Y selon le facteur cos(tilt).
   */
  correct(lm: FilteredLandmark): FilteredLandmark {
    const tilt = this.getTiltCompensation();
    if (Math.abs(tilt) < 0.05) return lm; // < 3° on ignore
    const factor = 1 / Math.max(0.5, Math.cos(tilt));
    // On centre la correction autour de y=0.5 pour éviter de pousser la tête hors cadre
    const ny = 0.5 + (lm.y - 0.5) * factor;
    return { x: lm.x, y: ny, z: lm.z, visibility: lm.visibility };
  }

  isActive(): boolean {
    return this.listening && Math.abs(90 - this.beta) > 3;
  }
}

// ═══════════════════════════════════════════════════════════════════════
// 3. LAYER SUBTRACTION — soustrait la marge tissu apparente
// ═══════════════════════════════════════════════════════════════════════
const LAYER_MARGINS_PX: Record<LayerType, number> = {
  tshirt: 5,
  shirt: 8,
  sweater: 15,
  jacket: 22,
  coat: 30,
};

export interface LayerSubtractionResult {
  active: boolean;
  detectedLayer: LayerType;
  subtractedPx: number;
  reason: string;
}

/**
 * Détecte la présence d'une couche textile :
 *   - Si shoulderWidth oscille de < 1 % alors que la torse semble "souple"
 *     (variation Y du milieu torse > 4 %), on suppose qu'il y a tissu mou.
 *   - On applique alors une marge de soustraction radiale.
 */
export function detectLayer(
  shoulderHistory: number[],
  torsoYHistory: number[]
): LayerSubtractionResult {
  if (shoulderHistory.length < 8) {
    return { active: false, detectedLayer: "tshirt", subtractedPx: 0, reason: "history-warmup" };
  }
  const shVar = variance(shoulderHistory) / Math.max(1, mean(shoulderHistory));
  const torsoVar = variance(torsoYHistory) / Math.max(1, mean(torsoYHistory));

  // Épaules très stables + torse mouvant → fabric soft → couche détectée
  if (shVar < 0.015 && torsoVar > 0.03) {
    let layer: LayerType = "shirt";
    if (torsoVar > 0.08) layer = "coat";
    else if (torsoVar > 0.06) layer = "jacket";
    else if (torsoVar > 0.045) layer = "sweater";
    return {
      active: true,
      detectedLayer: layer,
      subtractedPx: LAYER_MARGINS_PX[layer],
      reason: "fabric-detected",
    };
  }
  return { active: false, detectedLayer: "tshirt", subtractedPx: 0, reason: "tight-fit" };
}

function mean(a: number[]): number {
  let s = 0; for (const v of a) s += v; return s / a.length;
}
function variance(a: number[]): number {
  const m = mean(a);
  let s = 0; for (const v of a) s += (v - m) * (v - m);
  return s / a.length;
}

// ═══════════════════════════════════════════════════════════════════════
// 4. CALCUL DES MÉTRIQUES → confiance, jamais en chiffres
// ═══════════════════════════════════════════════════════════════════════
export function computeMetrics(
  landmarks: FilteredLandmark[],
  W: number,
  H: number,
  layer: LayerSubtractionResult,
  detectionStartMs: number
): ZeroSizeMetrics | null {
  if (!landmarks || landmarks.length < 33) return null;
  const lSh = landmarks[POSE_INDEX.L_SHOULDER];
  const rSh = landmarks[POSE_INDEX.R_SHOULDER];
  const lHip = landmarks[POSE_INDEX.L_HIP];
  const rHip = landmarks[POSE_INDEX.R_HIP];
  const lKnee = landmarks[POSE_INDEX.L_KNEE];
  const lAnkle = landmarks[POSE_INDEX.L_ANKLE];
  const lWrist = landmarks[POSE_INDEX.L_WRIST];

  if (!lSh || !rSh || !lHip || !rHip) return null;

  // Largeurs en px
  const shoulderWidth = Math.hypot((rSh.x - lSh.x) * W, (rSh.y - lSh.y) * H) - layer.subtractedPx;
  const hipWidth = Math.hypot((rHip.x - lHip.x) * W, (rHip.y - lHip.y) * H) - layer.subtractedPx * 0.6;
  const torsoLength = Math.abs(((lHip.y + rHip.y) / 2 - (lSh.y + rSh.y) / 2) * H);
  const inseam = lHip && lAnkle ? Math.abs((lAnkle.y - lHip.y) * H) : 0;
  const armLength = lSh && lWrist ? Math.hypot((lWrist.x - lSh.x) * W, (lWrist.y - lSh.y) * H) : 0;

  // Confiance : fonction de la visibility moyenne des points anatomiques clés
  const shoulderConfidence = clamp01((lSh.visibility + rSh.visibility) / 2);
  const hipConfidence = clamp01((lHip.visibility + rHip.visibility) / 2);
  const torsoConfidence = clamp01((shoulderConfidence + hipConfidence) / 2);
  const inseamConfidence = clamp01(((lKnee?.visibility ?? 0.6) + (lAnkle?.visibility ?? 0.5)) / 2);

  const lockScore = clamp01(
    shoulderConfidence * 0.35 +
    hipConfidence * 0.25 +
    torsoConfidence * 0.25 +
    inseamConfidence * 0.15
  );

  return {
    shoulderWidth,
    torsoLength,
    hipWidth,
    inseam,
    armLength,
    shoulderConfidence,
    torsoConfidence,
    hipConfidence,
    inseamConfidence,
    lockScore,
    layerCalibrationActive: layer.active,
    lockTimeMs: Math.round(performance.now() - detectionStartMs),
  };
}

function clamp01(v: number): number {
  return v < 0 ? 0 : v > 1 ? 1 : v;
}

/**
 * Convertit un score de confiance en libellé qualitatif francais —
 * utilisé par l'UI pour respecter la philosophie Zero-Size.
 */
export function fitLabel(confidence: number): string {
  if (confidence > 0.92) return "Ajustement parfait";
  if (confidence > 0.78) return "Ajustement précis";
  if (confidence > 0.6) return "Ajustement serré";
  if (confidence > 0.4) return "Calibrage en cours";
  return "Recherche du verrou";
}
