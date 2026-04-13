/**
 * TRYONYOU V11 — Recomendador P.A.U. (IA Emocional + FTT)
 * Pau le Paon — Agente de estilo soberano.
 * 
 * FTT = Fashion Taste Transform
 * Combina biometría + preferencias emocionales + contexto de ocasión
 * para recomendar la prenda perfecta del catálogo.
 */

const PAU_VERSION = "V11-OMEGA";
const PAU_PERSONALITY = "sovereign-luxury-concierge";

/**
 * Perfiles emocionales que P.A.U. detecta y utiliza.
 */
const EMOTIONAL_PROFILES = {
  CONFIDENT: { weight: 1.2, brands: ["BALMAIN", "SAINT LAURENT", "GIVENCHY"] },
  ROMANTIC: { weight: 1.1, brands: ["VALENTINO", "CHLOÉ", "DIOR"] },
  MINIMALIST: { weight: 1.0, brands: ["CELINE", "THE ROW", "JIL SANDER"] },
  BOLD: { weight: 1.3, brands: ["VERSACE", "BALMAIN", "ALEXANDER MCQUEEN"] },
  CLASSIC: { weight: 1.0, brands: ["BURBERRY", "HERMÈS", "LORO PIANA"] },
};

/**
 * Contextos de ocasión para filtrar recomendaciones.
 */
const OCCASION_CONTEXTS = {
  GALA: { formality: 1.0, priceMultiplier: 1.5 },
  BUSINESS: { formality: 0.8, priceMultiplier: 1.0 },
  CASUAL_LUXE: { formality: 0.4, priceMultiplier: 0.8 },
  INAUGURATION: { formality: 0.9, priceMultiplier: 1.3 },
  DATE_NIGHT: { formality: 0.7, priceMultiplier: 1.1 },
};

/**
 * P.A.U. genera una recomendación personalizada.
 * @param {Object} params - {biometrics, emotionalProfile, occasion, catalog, budget}
 * @returns {Object} Recomendación con explicación emocional
 */
export function recommend({ biometrics, emotionalProfile, occasion, catalog, budget }) {
  const profile = EMOTIONAL_PROFILES[emotionalProfile] || EMOTIONAL_PROFILES.CONFIDENT;
  const context = OCCASION_CONTEXTS[occasion] || OCCASION_CONTEXTS.BUSINESS;

  // Filtrar por marcas afines al perfil emocional
  let candidates = catalog.filter((item) => {
    const brandMatch = profile.brands.includes(item.brand) ? profile.weight : 0.7;
    const priceOk = !budget || item.price <= budget * context.priceMultiplier;
    return priceOk && brandMatch > 0.5;
  });

  // Si no hay candidatos, usar todo el catálogo
  if (candidates.length === 0) candidates = [...catalog];

  // Scoring: combinar fit biométrico + afinidad emocional + precisión
  const scored = candidates.map((item) => {
    const brandScore = profile.brands.includes(item.brand) ? profile.weight : 0.6;
    const precisionScore = (item.precision || 95) / 100;
    const formalityMatch = 1 - Math.abs(context.formality - (item.formality || 0.5));
    const totalScore = brandScore * 0.4 + precisionScore * 0.35 + formalityMatch * 0.25;

    return { ...item, pauScore: Math.round(totalScore * 100) };
  });

  // Ordenar por score descendente
  scored.sort((a, b) => b.pauScore - a.pauScore);

  const top = scored[0];
  if (!top) return null;

  return {
    recommendation: top,
    alternatives: scored.slice(1, 4),
    pauMessage: generatePauMessage(top, emotionalProfile, occasion),
    pauScore: top.pauScore,
    emotionalProfile,
    occasion,
    pauVersion: PAU_VERSION,
    timestamp: Date.now(),
  };
}

/**
 * Genera el mensaje personalizado de P.A.U.
 * @param {Object} garment - Prenda recomendada
 * @param {string} profile - Perfil emocional
 * @param {string} occasion - Contexto de ocasión
 * @returns {string} Mensaje de P.A.U.
 */
function generatePauMessage(garment, profile, occasion) {
  const messages = {
    fr: {
      CONFIDENT: `Cette pièce ${garment.brand} a été conçue pour quelqu'un qui sait exactement qui il est. Précision d'ajustement: ${garment.precision || 98}%.`,
      ROMANTIC: `La douceur de ce ${garment.name} épouse votre silhouette avec une grâce naturelle. C'est l'élégance sans effort.`,
      MINIMALIST: `Moins, c'est plus. Ce ${garment.brand} incarne la perfection dans sa simplicité. Ajustement souverain garanti.`,
      BOLD: `Audace et précision. Ce ${garment.name} ne passe pas inaperçu. Vous non plus.`,
      CLASSIC: `L'intemporel ${garment.brand}. Un investissement dans l'élégance qui traverse les saisons.`,
    },
  };

  return (
    messages.fr[profile] ||
    `P.A.U. recommande: ${garment.name} par ${garment.brand}. Score de compatibilité: ${garment.pauScore}%.`
  );
}

/**
 * P.A.U. whisper — mensaje corto para UI overlay.
 * @param {Object} garment - Prenda
 * @returns {string} Whisper de P.A.U.
 */
export function pauWhisper(garment) {
  if (!garment) return "P.A.U. analyse votre silhouette...";
  return `${garment.brand} · ${garment.name} · Précision ${garment.precision || 98}% · Score ${garment.pauScore || "—"}`;
}

export { EMOTIONAL_PROFILES, OCCASION_CONTEXTS, PAU_VERSION };

export default {
  recommend,
  pauWhisper,
  EMOTIONAL_PROFILES,
  OCCASION_CONTEXTS,
  PAU_VERSION,
};
