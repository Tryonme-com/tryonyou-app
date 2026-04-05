/**
 * Shopify Checkout — Protocolo Transacción Divineo V10.5
 * INTEGRACIÓN: SHOPIFY ADMIN API + TRYONYOU BIOMETRICS
 * "Conversión sin fricción: Del escaneo al pago."
 *
 * El hash biométrico queda vinculado al pedido como `_Sovereignty_ID`.
 * Los tokens secretos se mantienen en el backend; el cliente sólo recibe la URL.
 */

export type ShopifyCheckoutResponse = {
  checkout_primary_url?: string;
  checkout_shopify_url?: string;
  checkout_amazon_url?: string;
  emotional_seal?: string;
};

/**
 * Crea el checkout perfecto vinculando el hash biométrico al pedido Shopify (Zero-Size).
 * Delega al API de backend (Admin API + storefront) para evitar exponer tokens en el cliente.
 *
 * @param biometricHash - Hash de la silueta biométrica (_Sovereignty_ID en el pedido).
 * @param fabricSensation - Etiqueta de ajuste de tejido (elastic label) para el protocolo Zero-Size.
 * @param code - Código de campaña/acceso opcional.
 */
export async function createPerfectCheckout(
  biometricHash: string,
  fabricSensation?: string,
  code?: string,
): Promise<void> {
  const payload: Record<string, unknown> = {
    biometric_hash: biometricHash,
    fabric_sensation: fabricSensation ?? "",
    protocol: "zero_size",
    shopping_flow: "non_stop_card",
    anti_accumulation: true,
    single_size_certitude: true,
  };
  if (code) payload.code = code;

  try {
    const r = await fetch("/api/v1/checkout/perfect-selection", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    if (!r.ok) {
      console.error("ERROR DE CONVERSIÓN: BLOQUEO DE LOGÍSTICA INVISIBLE.");
      return;
    }

    const j = (await r.json()) as ShopifyCheckoutResponse;

    if (j.emotional_seal) {
      window.alert(j.emotional_seal);
    }

    const primary = j.checkout_primary_url?.trim();
    const shop = j.checkout_shopify_url?.trim();
    const amz = j.checkout_amazon_url?.trim();
    const url = primary || shop || amz;

    if (url) {
      window.open(url, "_blank", "noopener,noreferrer");
      return;
    }

    // Fallback: URL pública configurada vía VITE_ (sin tokens secretos en cliente).
    const checkoutBase = (
      import.meta.env.VITE_SHOPIFY_PERFECT_CHECKOUT_URL ?? ""
    ).trim();
    const variantId = (
      import.meta.env.VITE_SHOPIFY_ZERO_SIZE_VARIANT_ID ?? ""
    ).trim();

    if (checkoutBase && variantId) {
      const sep = checkoutBase.includes("?") ? "&" : "?";
      window.location.href = `${checkoutBase}${sep}variant=${variantId}`;
      return;
    }

    if (!j.emotional_seal) {
      window.alert(
        "Parcours enregistré — les ponts marchands seront actifs dès configuration serveur (Zero-Size).",
      );
    }
  } catch (error) {
    console.error("ERROR DE CONVERSIÓN: BLOQUEO DE LOGÍSTICA INVISIBLE.", error);
  }
}
