/** 🛡️ EJECUCIÓN DE CHECKOUT V10.5
 * OBJETIVO: Cero fricción. Cero tallas. Margen Blindado.
 */

export const triggerPerfectSnap = (variantId: string, biometricHash: string): void => {
  console.log("PA, PA, PA - INYECTANDO VARIANTE SOBERANA EN EL CARRITO...");

  // 1. Construcción de la URL de Certeza
  const shopifyStore = import.meta.env.VITE_STORE_DOMAIN;
  const checkoutPath = import.meta.env.VITE_SHOPIFY_PERFECT_CHECKOUT_URL;

  if (!shopifyStore || !checkoutPath) {
    console.warn(
      "[checkoutEngine] triggerPerfectSnap: VITE_STORE_DOMAIN or VITE_SHOPIFY_PERFECT_CHECKOUT_URL is not configured.",
    );
    return;
  }

  // 2. Parámetros de Soberanía (Atributos de Pedido)
  const checkoutUrl = new URL(`${shopifyStore}${checkoutPath}`);
  checkoutUrl.searchParams.append("variant", variantId);
  checkoutUrl.searchParams.append("quantity", "1");
  checkoutUrl.searchParams.append("attributes[Sovereignty_ID]", biometricHash);
  checkoutUrl.searchParams.append(
    "attributes[Patent]",
    import.meta.env.VITE_PATENT_ID ?? "",
  );

  // 3. Redirección Inmediata al Búnker de Pago
  // Usamos replace para que el usuario no pueda volver atrás a la 'lotería' de tallas
  window.location.replace(checkoutUrl.toString());
};
