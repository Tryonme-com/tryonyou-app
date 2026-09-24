/** Protocolo Divineo V11.0 — tallas, oro, biometría mano, malla Firebase. */

export const PROTOCOL_DIVINEO_VERSION = "11.0" as const;

/** Oro Divineo — bordes / acentos UI. */
export const ORO_DIVINEO = "#D4AF37" as const;

export const SOVEREIGN_FIT_LABEL = "Sovereign Fit" as const;

/** MediaPipe mano: 21 puntos por mano (mano derecha/izquierda = pipelines separados). */
export const HAND_LANDMARK_COUNT = 21 as const;

/** Nombre de asset malla (Firebase Storage / CDN); ~111MB — no commitear. */
export const NINA_PERFECTA_MESH_FILENAME = "nina_perfecta_mesh.json" as const;

export const FORBIDDEN_CLASSICAL_SIZES = ["S", "M", "L", "XS", "XL", "XXL"] as const;

export function isForbiddenSizeToken(s: string): boolean {
  const t = s.trim().toUpperCase();
  return (FORBIDDEN_CLASSICAL_SIZES as readonly string[]).includes(t);
}
