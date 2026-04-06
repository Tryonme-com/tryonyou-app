/**
 * 🔗 INTEGRACIÓN LINEAR — PROTOCOLO V10 OMEGA
 * Sincronización Directa: ZeroSizeEngine → Make.com → Shopify/Instagram
 *
 * Patente: PCT/EP2025/067317 — @CertezaAbsoluta @lo+erestu
 * Bajo Protocolo de Soberanía V10 — Founder: Rubén
 *
 * Variables de entorno (al menos una debe estar definida):
 *   VITE_MAKE_WEBHOOK_URL          (preferida en build Vite)
 *   MAKE_WEBHOOK_URL               (fallback)
 *   VITE_MAKE_ESPEJO_WEBHOOK_URL   (alternativa espejo)
 *
 * En entorno serverless/Node el módulo lee process.env;
 * en build Vite los valores son inyectados en compile-time por Vite.
 */

import { ZeroSizeEngine, type ScanData, type SovereignFitResult } from "./zeroSizeEngine";

const PATENTE = "PCT/EP2025/067317";

export type SyncSovereigntyResult = {
  ok: boolean;
  fit?: SovereignFitResult;
  upstreamStatus?: number;
  error?: string;
};

function _makeWebhookUrl(): string {
  // Vite injects VITE_* variables; non-VITE vars are only available in Node/SSR contexts.
  const candidates = [
    typeof import.meta !== "undefined" &&
      (import.meta as Record<string, unknown>).env
      ? ((import.meta as { env: Record<string, string> }).env
          .VITE_MAKE_WEBHOOK_URL ?? "")
      : "",
    typeof import.meta !== "undefined" &&
      (import.meta as Record<string, unknown>).env
      ? ((import.meta as { env: Record<string, string> }).env
          .VITE_MAKE_ESPEJO_WEBHOOK_URL ?? "")
      : "",
    typeof process !== "undefined" && process.env
      ? (process.env["MAKE_WEBHOOK_URL"] ?? "")
      : "",
    typeof process !== "undefined" && process.env
      ? (process.env["MAKE_ESPEJO_WEBHOOK_URL"] ?? "")
      : "",
  ];
  return candidates.find((v) => v.trim().startsWith("http")) ?? "";
}

/**
 * Sincroniza los datos de escaneo biométrico con la nube de Make.com.
 * Implementa el Protocolo V10 Omega: ZeroSizeEngine → Make.com.
 *
 * @param scanData - Datos de escaneo biométrico (pecho, hombro, cintura…)
 * @returns Resultado de la sincronización.
 */
export async function syncSovereignty(
  scanData: ScanData,
): Promise<SyncSovereigntyResult> {
  const engine = new ZeroSizeEngine(scanData);
  const fit = engine.calculateSovereignFit();

  const url = _makeWebhookUrl();
  if (!url) {
    return {
      ok: false,
      fit,
      error:
        "MAKE_WEBHOOK_URL no configurada. Define VITE_MAKE_WEBHOOK_URL o MAKE_WEBHOOK_URL.",
    };
  }

  const payload = {
    patente: PATENTE,
    fit,
    timestamp: new Date().toISOString(),
    status: "Soberanía Confirmada",
  };

  try {
    const response = await fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    if (response.ok) {
      return { ok: true, fit, upstreamStatus: response.status };
    }

    return {
      ok: false,
      fit,
      upstreamStatus: response.status,
      error: `Make webhook devolvió estado ${response.status}`,
    };
  } catch (err) {
    const message = err instanceof Error ? err.message : String(err);
    return { ok: false, fit, error: message };
  }
}
