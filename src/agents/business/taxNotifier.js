/**
 * Agent #02 — Tax Notifier
 * Notificaciones fiscales y compliance para operaciones en Francia.
 */

const TVA_RATE_FR = 0.20;
const MICRO_ENTERPRISE_LIMIT = 77700;

export function calculateTVA(amountHT) {
  return {
    ht: amountHT,
    tva: Math.round(amountHT * TVA_RATE_FR * 100) / 100,
    ttc: Math.round(amountHT * (1 + TVA_RATE_FR) * 100) / 100,
    rate: TVA_RATE_FR,
  };
}

export function checkMicroEnterpriseLimits(yearlyRevenue) {
  const remaining = MICRO_ENTERPRISE_LIMIT - yearlyRevenue;
  return {
    yearlyRevenue,
    limit: MICRO_ENTERPRISE_LIMIT,
    remaining: Math.max(0, remaining),
    exceeded: yearlyRevenue > MICRO_ENTERPRISE_LIMIT,
    alert: remaining < 5000 ? "ATTENTION: Proche du plafond micro-entreprise" : null,
  };
}

export function generateInvoice({ client, amount, description, date }) {
  return {
    invoiceId: `FAC-${new Date(date || Date.now()).getFullYear()}-${String(Math.floor(Math.random() * 9999)).padStart(4, "0")}`,
    client,
    amountHT: amount,
    tva: Math.round(amount * TVA_RATE_FR * 100) / 100,
    amountTTC: Math.round(amount * (1 + TVA_RATE_FR) * 100) / 100,
    description,
    date: date || new Date().toISOString(),
    status: "draft",
  };
}

export default { calculateTVA, checkMicroEnterpriseLimits, generateInvoice };
