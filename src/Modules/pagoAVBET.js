/**
 * TRYONYOU V11 — Pasarela Biométrica AVBET (Iris + Voz)
 * Pago soberano en EUR sin intermediarios de talla.
 * 
 * Flujo: Contrato → Firma biométrica → Pago Stripe
 * Las marcas pagan a TryOnYou (no al revés).
 */

const STRIPE_MODES = {
  INAUGURATION: "inauguration",
  LAFAYETTE: "lafayette",
  SUBSCRIPTION: "subscription",
  PILOT: "pilot",
};

const PLANS = {
  PILOTE: {
    id: "pilote",
    name: "Pilote Gratuit",
    nameFr: "Pilote Gratuit — 1er mois",
    price: 0,
    commission: 0.03, // 3% desde día 1
    description: "1er mois gratuit + 3% commission sur les ventes dès le 1er jour",
  },
  DIVINEO_PRO: {
    id: "divineo_pro",
    name: "Divineo Pro",
    nameFr: "Divineo Pro",
    price: 29900, // 299€/mes en centimes
    commission: 0.03,
    description: "Accès complet au miroir digital + analytics + support prioritaire",
  },
  ENTERPRISE: {
    id: "enterprise",
    name: "Enterprise Lafayette",
    nameFr: "Enterprise Lafayette",
    price: 109900, // 1099€/mes en centimes
    commission: 0.08, // 8% royalties
    description: "Déploiement premium avec orchestration P.A.U. complète",
  },
};

/**
 * Genera URL de checkout Stripe para un plan específico.
 * @param {string} planId - ID del plan (pilote, divineo_pro, enterprise)
 * @param {string} email - Email del cliente
 * @returns {string} URL de Stripe Checkout
 */
export function generateCheckoutUrl(planId, email) {
  const plan = Object.values(PLANS).find((p) => p.id === planId);
  if (!plan) throw new Error(`[AVBET] Plan inconnu: ${planId}`);

  const baseUrl = import.meta.env.VITE_STRIPE_CHECKOUT_URL || "https://checkout.stripe.com";
  const params = new URLSearchParams({
    plan: plan.id,
    amount: plan.price.toString(),
    currency: "eur",
    email: email || "",
    success_url: `${window.location.origin}/success`,
    cancel_url: `${window.location.origin}/cancel`,
  });

  return `${baseUrl}?${params.toString()}`;
}

/**
 * Valida firma biométrica antes del pago.
 * Simula verificación de iris + voz para autorizar transacción.
 * @param {Object} biometricData - Datos biométricos del usuario
 * @returns {Object} Resultado de validación
 */
export function validateBiometricSignature(biometricData) {
  if (!biometricData || !biometricData.precision) {
    return { valid: false, reason: "Données biométriques manquantes" };
  }

  if (biometricData.precision < 0.95) {
    return { valid: false, reason: "Précision insuffisante pour autorisation" };
  }

  return {
    valid: true,
    token: `AVBET-${Date.now()}-${Math.random().toString(36).slice(2, 10)}`,
    method: "iris+voice",
    precision: biometricData.precision,
    timestamp: Date.now(),
    sovereign: true,
    currency: "EUR",
  };
}

/**
 * Flujo completo de pago: Contrato → Firma → Stripe
 * @param {Object} params - {planId, email, biometricData, contractSigned}
 * @returns {Object} Resultado del flujo
 */
export function initiatePaymentFlow({ planId, email, biometricData, contractSigned }) {
  // Paso 1: Verificar contrato firmado
  if (!contractSigned) {
    return {
      success: false,
      step: "contract",
      message: "Le contrat doit être signé avant le paiement.",
    };
  }

  // Paso 2: Validar firma biométrica
  const bioAuth = validateBiometricSignature(biometricData);
  if (!bioAuth.valid) {
    return {
      success: false,
      step: "biometric",
      message: bioAuth.reason,
    };
  }

  // Paso 3: Generar checkout
  const checkoutUrl = generateCheckoutUrl(planId, email);

  return {
    success: true,
    step: "checkout",
    checkoutUrl,
    bioToken: bioAuth.token,
    message: "Redirection vers Stripe Checkout...",
  };
}

/**
 * Calcula comisión sobre ventas para un período.
 * @param {number} salesAmount - Montant des ventes en EUR
 * @param {string} planId - ID del plan
 * @returns {Object} Détail de la commission
 */
export function calculateCommission(salesAmount, planId) {
  const plan = Object.values(PLANS).find((p) => p.id === planId);
  if (!plan) return null;

  const commission = salesAmount * plan.commission;
  return {
    salesAmount,
    rate: plan.commission,
    commission: Math.round(commission * 100) / 100,
    plan: plan.nameFr,
    currency: "EUR",
  };
}

export { STRIPE_MODES, PLANS };

export default {
  generateCheckoutUrl,
  validateBiometricSignature,
  initiatePaymentFlow,
  calculateCommission,
  STRIPE_MODES,
  PLANS,
};
