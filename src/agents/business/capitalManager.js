/**
 * Agent #01 — Capital Manager
 * Gestión de capital, revenue tracking y proyecciones financieras.
 * Parte del equipo de 52 agentes de producción.
 */

export function trackRevenue({ source, amount, currency = "EUR", timestamp }) {
  return {
    id: `REV-${Date.now()}`,
    source,
    amount,
    currency,
    timestamp: timestamp || Date.now(),
    validated: true,
  };
}

export function projectMonthlyRevenue(dailyAverage, daysRemaining) {
  return {
    projected: Math.round(dailyAverage * daysRemaining),
    dailyAverage,
    daysRemaining,
    currency: "EUR",
    confidence: 0.85,
  };
}

export function calculateBurnRate(expenses, revenue, months = 3) {
  const monthlyBurn = expenses / months;
  const monthlyRevenue = revenue / months;
  const runway = monthlyRevenue > monthlyBurn
    ? Infinity
    : Math.round((revenue - expenses) / monthlyBurn);

  return { monthlyBurn, monthlyRevenue, runway, healthy: runway > 6 };
}

export default { trackRevenue, projectMonthlyRevenue, calculateBurnRate };
