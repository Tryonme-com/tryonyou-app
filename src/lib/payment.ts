import { getAbvetosSovereignPaymentUrl, getInaugurationStripeCheckoutUrl } from "./lafayetteCheckout";
import { fetchParisInaugurationCheckoutUrl } from "../services/paymentService";
import QRCode from "qrcode";

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
  throw new Error("Secure random generator unavailable for snap token.");
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
  const qrImageUrl = await QRCode.toDataURL(paymentUrl, {
    width: 280,
    margin: 1,
    errorCorrectionLevel: "M",
  });
  const expiresAt = new Date(Date.now() + QR_EXPIRATION_MS).toISOString();

  return { paymentUrl, qrImageUrl, expiresAt };
}
