/**
 * Fabric Fit Comparator + elasticidad (protocolo Zero-Size: sin tallas ni medidas corpóreas en UI).
 * Métricas derivadas de landmarks normalizados (MediaPipe) — referencias relativas, no absolutas.
 */

export type NormalizedLandmark = {
  x: number;
  y: number;
  z?: number;
  visibility?: number;
};

function dist2(a: NormalizedLandmark, b: NormalizedLandmark): number {
  const dx = a.x - b.x;
  const dy = a.y - b.y;
  return Math.hypot(dx, dy);
}

/** Ratio hombro/cadera en espacio normalizado (proxy de elasticidad de silueta). */
export function computeElasticityRatio(landmarks: NormalizedLandmark[]): number {
  if (!landmarks || landmarks.length < 25) return 0.5;
  const shoulder = dist2(landmarks[11], landmarks[12]);
  const hip = dist2(landmarks[23], landmarks[24]);
  return shoulder / Math.max(hip, 1e-6);
}

export type FabricFitVerdict = "aligned" | "drape_bias" | "tension_bias";

/** Compara la elasticidad suavizada (EMA) frente a una banda de referencia de tejido (sin tallas). */
export function fabricFitComparator(
  elasticityEma: number,
  band: [number, number] = [0.82, 1.18],
): FabricFitVerdict {
  if (elasticityEma >= band[0] && elasticityEma <= band[1]) return "aligned";
  if (elasticityEma < band[0]) return "drape_bias";
  return "tension_bias";
}

export function verdictToUiLabel(v: FabricFitVerdict): string {
  switch (v) {
    case "aligned":
      return "Cohérence drape — tenue";
    case "drape_bias":
      return "Préférence drapé";
    case "tension_bias":
      return "Préférence tenue";
    default:
      return "Analyse en cours";
  }
}
