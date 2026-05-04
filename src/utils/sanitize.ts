/**
 * Protocolo Zero-Size — elimina referencias a tallas convencionales
 * en cualquier objeto de datos antes de exponerlo en la interfaz.
 *
 * Operates on the data structure directly (not on raw JSON text) to avoid
 * corrupting property names, unrelated abbreviations, or JSON syntax.
 */

const SOVEREIGN_LABEL = "AJUSTE SOBERANO";

/**
 * Replaces forbidden clothing-size words inside a single string value.
 * Uses word boundaries so 'GLASS' or 'SMALL' are left untouched.
 */
function sanitizeString(value: string): string {
  return value.replace(/\b(XXL|XL|L|M|S|Talla|Size)\b/gi, SOVEREIGN_LABEL);
}

/** Recursively traverses a value and sanitizes string leaves. */
function sanitizeValue(value: unknown): unknown {
  if (typeof value === "string") return sanitizeString(value);
  if (Array.isArray(value)) return value.map(sanitizeValue);
  if (value !== null && typeof value === "object") {
    return Object.fromEntries(
      Object.entries(value as Record<string, unknown>).map(([k, v]) => [k, sanitizeValue(v)]),
    );
  }
  return value;
}

export const sanitizeOutput = <T>(data: T): T => sanitizeValue(data) as T;


