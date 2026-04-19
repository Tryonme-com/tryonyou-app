import { isForbiddenSizeToken } from "../divineo/divineoV11Config";

export const V9_IDENTITY_LABEL = "V9 Identity" as const;

const FORBIDDEN_NUMERIC_SIZE_REGEX = /\b(?:32|34|36|38|40|42|44|46|48|50)\b/;
const BODY_MEASURE_REGEX =
  /\b(?:\d{2,3}(?:[.,]\d+)?\s*(?:cm|kg)|pecho|cintura|cadera|busto|chest|waist|hip|shoulder)\b/i;

function hasForbiddenToken(value: string): boolean {
  const tokens = value
    .split(/[^a-zA-Z0-9]+/)
    .map((token) => token.trim())
    .filter(Boolean);
  return tokens.some((token) => isForbiddenSizeToken(token));
}

/**
 * Privacy Firewall (patente PCT/EP2025/067317):
 * bloquea tallas tradicionales y medidas corporales en texto renderizable.
 */
export function enforceV9IdentityLabel(raw: string): string {
  const normalized = String(raw || "").trim();
  if (!normalized) return V9_IDENTITY_LABEL;
  if (hasForbiddenToken(normalized)) return V9_IDENTITY_LABEL;
  if (FORBIDDEN_NUMERIC_SIZE_REGEX.test(normalized)) return V9_IDENTITY_LABEL;
  if (BODY_MEASURE_REGEX.test(normalized)) return V9_IDENTITY_LABEL;
  return normalized;
}

export function sanitizeRenderPayload(payload: Record<string, unknown>): Record<string, unknown> {
  const next: Record<string, unknown> = {};
  for (const [key, value] of Object.entries(payload)) {
    if (typeof value === "string") {
      next[key] = enforceV9IdentityLabel(value);
      continue;
    }
    next[key] = value;
  }
  return next;
}
