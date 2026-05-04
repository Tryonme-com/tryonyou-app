/**
 * Protocolo Zero-Size — elimina referencias a tallas convencionales
 * en cualquier objeto de datos antes de exponerlo en la interfaz.
 */

const FORBIDDEN_SIZE_PATTERNS: RegExp[] = [
  /\bXXL\b/gi,
  /\bXL\b/gi,
  /\bL\b/g,
  /\bM\b/g,
  /\bS\b/g,
  /\bTalla\b/gi,
  /\bSize\b/gi,
];

const SOVEREIGN_LABEL = "AJUSTE SOBERANO";

export const sanitizeOutput = <T>(data: T): T => {
  let cleanData = JSON.stringify(data);

  FORBIDDEN_SIZE_PATTERNS.forEach((pattern) => {
    cleanData = cleanData.replace(pattern, SOVEREIGN_LABEL);
  });

  return JSON.parse(cleanData) as T;
};
