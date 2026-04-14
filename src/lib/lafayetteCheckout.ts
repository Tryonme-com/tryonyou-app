/**
 * Utilidades de pago: checkout soberano Divineo (abvetos.com) + IBAN transfer.
 * V11 Rive Gauche: bloqueo de cobros externos fuera de dominio permitido.
 */
import {
  ABVETOS_LIVE_SHOP_VARIANT_ID,
  getDivineoCheckoutUrl,
  isDivineoCheckoutUrlAllowed,
} from "../divineo/envBootstrap";

export { ABVETOS_LIVE_SHOP_VARIANT_ID };

export type IbanTransferDetails = {
  method: string;
  entity: string;
  siret: string;
  iban: string;
  bic: string;
  amount_eur: number;
  amount_label: string;
  currency: string;
  bank: string;
  iban_configured: boolean;
  note: string;
};

export type ProformaInvoice = {
  ref: string;
  from: string;
  to: string;
  amount_eur: number;
  currency: string;
  note: string;
  status: string;
};

export type IbanTransferResponse = {
  status: string;
  transfer: IbanTransferDetails;
  invoice: ProformaInvoice;
  message: string;
};

export async function fetchIbanTransferDetails(
  amountKey?: string,
): Promise<IbanTransferDetails | null> {
  try {
    const qs = amountKey ? `?amount=${encodeURIComponent(amountKey)}` : "";
    const r = await fetch(`/api/v1/payment/iban-transfer${qs}`);
    if (!r.ok) return null;
    const j = (await r.json()) as IbanTransferDetails & { status: string };
    if (j.status !== "ok") return null;
    return j;
  } catch {
    return null;
  }
}

export async function initiateIbanTransfer(
  amountKey?: string,
  to?: string,
): Promise<IbanTransferResponse | null> {
  try {
    const r = await fetch("/api/v1/payment/iban-transfer", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        amount_key: amountKey || "total_immediate",
        to: to || "Le Bon Marché Rive Gauche",
      }),
    });
    if (!r.ok) return null;
    const j = (await r.json()) as IbanTransferResponse;
    if (j.status !== "ok") return null;
    return j;
  } catch {
    return null;
  }
}

export function getDivineoSovereignCheckoutUrl(): string {
  const e = import.meta.env;
  const candidates = [
    e.VITE_STRIPE_CHECKOUT_URL,
    e.VITE_INAUGURATION_STRIPE_CHECKOUT_URL,
    e.VITE_STRIPE_LINK_SOVEREIGNTY_4_5M,
    e.VITE_STRIPE_LINK_SOVEREIGNTY_98K,
  ];
  for (const v of candidates) {
    const s = (v as string | undefined)?.trim();
    if (s && isDivineoCheckoutUrlAllowed(s)) return s;
  }
  return "";
}

/** Solo `VITE_INAUGURATION_STRIPE_CHECKOUT_URL` (build / Vercel). */
export function getInaugurationStripeEnvUrl(): string {
  const candidate = (
    import.meta.env.VITE_INAUGURATION_STRIPE_CHECKOUT_URL as string | undefined
  )?.trim();
  if (!candidate) return "";
  return isDivineoCheckoutUrlAllowed(candidate) ? candidate : "";
}

/** Inauguración 12.500 € — primero env inaugural; respaldos soberanos (liquidez). */
export function getInaugurationStripeCheckoutUrl(): string {
  const direct = getInaugurationStripeEnvUrl();
  if (direct) return direct;
  return getDivineoSovereignCheckoutUrl();
}

/**
 * Variante Shopify usada en cobros: env primero, si no el SKU LIVE abvetos (53412065182103).
 */
export function resolveShopifyVariantIdForPayments(): string {
  const fromEnv = (import.meta.env.VITE_SHOP_VARIANT as string | undefined)?.trim();
  return fromEnv || ABVETOS_LIVE_SHOP_VARIANT_ID;
}

/**
 * URL de carrito abvetos.com acorde a `getDivineoCheckoutUrl()` (variant ya fijado por env o ID soberano).
 */
export function getAbvetosSovereignPaymentUrl(): string {
  return getDivineoCheckoutUrl();
}

/**
 * Abre un enlace de pago en nueva pestaña (Stripe Payment Link o URL externa).
 */
export function openPaymentUrl(url: string): boolean {
  const u = url.trim();
  if (!u || !isDivineoCheckoutUrlAllowed(u)) return false;
  window.open(u, "_blank", "noopener,noreferrer");
  return true;
}

/**
 * Cobro inaugural: prioridad absoluta `VITE_INAUGURATION_STRIPE_CHECKOUT_URL`.
 * Sin validación Shopify ni pasos extra que bloqueen (Firebase puede seguir sincronizando).
 */
export function openInaugurationStripeLiquidity(): void {
  const url = getInaugurationStripeCheckoutUrl();
  if (!url) return;
  openPaymentUrl(url);
}
