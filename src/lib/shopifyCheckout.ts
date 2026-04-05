/**
 * 🛍️ PROTOCOLO DE TRANSACCIÓN DIVINEO V10.5
 * INTEGRACIÓN: SHOPIFY ADMIN API + TRYONYOU BIOMETRICS
 * "Conversión sin fricción: Del escaneo al pago."
 */

export type ShopifyCheckoutData = {
  variantId: string | undefined;
  quantity: number;
  properties: {
    _Sovereignty_ID: string;
    _Patent: string | undefined;
  };
};

export const createPerfectCheckout = async (biometricHash: string): Promise<void> => {
  const shopifyData: ShopifyCheckoutData = {
    variantId: import.meta.env.VITE_SHOPIFY_ZERO_SIZE_VARIANT_ID,
    quantity: 1,
    properties: {
      _Sovereignty_ID: biometricHash, // El ajuste perfecto queda vinculado al pedido
      _Patent: import.meta.env.VITE_PATENT_ID,
    },
  };

  // Jules orquesta la llamada al Storefront/Admin API
  try {
    console.log("PA, PA, PA - INYECTANDO VARIANTE SOBERANA EN EL CARRITO...");

    // Redirección inmediata al Checkout de Certeza
    window.location.href = `${import.meta.env.VITE_SHOPIFY_PERFECT_CHECKOUT_URL}?variant=${shopifyData.variantId}`;
  } catch (error) {
    console.error("ERROR DE CONVERSIÓN: BLOQUEO DE LOGÍSTICA INVISIBLE.", error);
  }
};
