/**
 * Mapa numérico PAU ↔ archivos en `public/assets/animations/`.
 * El “Chasquido” instantáneo usa `CHASQUIDO` → `pau_01_chasquido.json` vía `getPauAnimationPath`.
 *
 * Opcional: `VITE_UI_ANIMATION` fuerza una ruta absoluta de un solo asset (override).
 *
 * Patente: PCT/EP2025/067317 — Bajo Protocolo de Soberanía V10 - Founder: Rubén
 */

/** IDs enteros — deben coincidir con el prefijo `pau_XX_` en el nombre de fichero. */
export const PAU_ANIMATIONS = {
  CHASQUIDO: 1,
  GREETING: 2,
  SCANNING: 3,
} as const;

export type PauAnimationId = (typeof PAU_ANIMATIONS)[keyof typeof PAU_ANIMATIONS];

const SLUG: Record<PauAnimationId, string> = {
  [PAU_ANIMATIONS.CHASQUIDO]: "chasquido",
  [PAU_ANIMATIONS.GREETING]: "saludo",
  [PAU_ANIMATIONS.SCANNING]: "escaneo",
};

/** Ruta pública final (Vite sirve `public/` en la raíz). */
export function getPauAnimationPath(id: PauAnimationId): string {
  const single = import.meta.env.VITE_UI_ANIMATION?.trim();
  if (single) {
    return single.startsWith("/") ? single : `/${single}`;
  }
  const n = String(id).padStart(2, "0");
  const slug = SLUG[id];
  return `/assets/animations/pau_${n}_${slug}.json`;
}
