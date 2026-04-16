import { getAbvetosSovereignPaymentUrl, getInaugurationStripeCheckoutUrl } from "./lafayetteCheckout";
import { fetchParisInaugurationCheckoutUrl } from "../services/paymentService";

const QR_EXPIRATION_MS = 2 * 60 * 1000;

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
  const bytes = new Uint8Array(16);
  if (typeof crypto !== "undefined" && typeof crypto.getRandomValues === "function") {
    crypto.getRandomValues(bytes);
    return Array.from(bytes, (b) => b.toString(16).padStart(2, "0")).join("");
  }
  return `${Date.now()}`;
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
  const expiresAt = new Date(Date.now() + QR_EXPIRATION_MS).toISOString();

  return { paymentUrl, qrImageUrl, expiresAt };
}
