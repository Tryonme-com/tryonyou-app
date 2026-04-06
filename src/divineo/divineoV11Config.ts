/** Protocolo Divineo V11 — tallas y marca de ajuste. */

export const ORO_DIVINEO = "#D4AF37" as const;

export const SOVEREIGN_FIT_LABEL = "Sovereign Fit" as const;

export const FORBIDDEN_CLASSICAL_SIZES = ["S", "M", "L", "XS", "XL", "XXL"] as const;

export function isForbiddenSizeToken(s: string): boolean {
  const t = s.trim().toUpperCase();
  return (FORBIDDEN_CLASSICAL_SIZES as readonly string[]).includes(t);
}
