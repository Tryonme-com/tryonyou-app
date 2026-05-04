/** 🛍️ MOTOR DE COMERCIO SEGURO
 * Valida dominios y variantes antes de la ejecución.
 * PATENTE: PCT/EP2025/067317
 */

const AUTHORIZED_DOMAIN = "abvetos.com";

export const executeSovereignCheckout = (variantId) => {
  const domain = import.meta.env.VITE_SHOP_DOMAIN;

  // 1. Validación de Seguridad - Recomendación Auditoría 3
  if (!variantId || !domain || domain !== AUTHORIZED_DOMAIN) {
    console.error("VULGARIZACIÓN DETECTADA: DOMINIO NO AUTORIZADO.");
    return;
  }

  // 2. Redirección Atómica
  const checkoutUrl = `https://${domain}/cart/${variantId}:1`;
  window.location.replace(checkoutUrl);
};

export default {
  executeSovereignCheckout,
  AUTHORIZED_DOMAIN,
};
