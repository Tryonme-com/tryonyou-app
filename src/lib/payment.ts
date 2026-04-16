import { getAbvetosSovereignPaymentUrl, getInaugurationStripeCheckoutUrl } from "./lafayetteCheckout";
import { fetchParisInaugurationCheckoutUrl } from "../services/paymentService";

export type AdvbetQR = {
  paymentUrl: string;
  qrImageUrl: string;
  expiresAt: string;
};

type GenerateAdvbetQROptions = {
  sessionId?: string;
  district?: string;
  snapToken?: string;
};

function buildSnapToken(): string {
  if (typeof crypto !== "undefined" && typeof crypto.randomUUID === "function") {
    return crypto.randomUUID();
  }
  return `${Date.now()}-${Math.random().toString(36).slice(2, 10)}`;
}

function decoratePaymentUrl(
  baseUrl: string,
  options: GenerateAdvbetQROptions,
  nowIso: string,
): string {
  try {
    const url = new URL(baseUrl);
    url.searchParams.set("snap", options.snapToken ?? buildSnapToken());
    if (options.sessionId) url.searchParams.set("session_id", options.sessionId);
    if (options.district) url.searchParams.set("district", options.district);
    url.searchParams.set("ts", nowIso);
    return url.toString();
  } catch {
    return baseUrl;
  }
}

export async function generateAdvbetQR(
  options: GenerateAdvbetQROptions = {},
): Promise<AdvbetQR | null> {
  const dynamic = await fetchParisInaugurationCheckoutUrl();
  const paymentBase =
    dynamic ||
    getInaugurationStripeCheckoutUrl().trim() ||
    getAbvetosSovereignPaymentUrl().trim();

  if (!paymentBase) return null;

  const nowIso = new Date().toISOString();
  const paymentUrl = decoratePaymentUrl(paymentBase, options, nowIso);
  const qrImageUrl = `https://api.qrserver.com/v1/create-qr-code/?size=280x280&data=${encodeURIComponent(paymentUrl)}`;
  const expiresAt = new Date(Date.now() + 2 * 60 * 1000).toISOString();

  return { paymentUrl, qrImageUrl, expiresAt };
}
