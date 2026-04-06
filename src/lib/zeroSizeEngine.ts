/**
 * ZeroSizeEngine — Protocolo V10 Omega
 * Calcula el ajuste soberano a partir de datos de escaneo biométrico.
 * Patente: PCT/EP2025/067317 — @CertezaAbsoluta @lo+erestu
 *
 * Protocolo Zero-Size: las medidas corporales brutas no se exponen en el resultado;
 * sólo se devuelven ratios y descriptores normalizados.
 */

export type ScanData = {
  chest?: number;
  shoulder?: number;
  waist?: number;
  hip?: number;
  height?: number;
  [key: string]: number | undefined;
};

export type SovereignFitResult = {
  /** Ratio torso (hombro / pecho normalizado). */
  torsoRatio: number;
  /** Índice de silueta (pecho / cadera, o pecho / cintura si no hay cadera). */
  silhouetteIndex: number;
  /** Descriptor cualitativo del ajuste sin revelar tallas ni medidas absolutas. */
  fitDescriptor: "sovereign_fit" | "drape_bias" | "tension_bias" | "insufficient_data";
  patente: string;
  protocol: string;
};

const PATENTE = "PCT/EP2025/067317";
const PROTOCOL = "ZeroSize-V10-Omega";

/** Banda de referencia para silhouetteIndex considerado «ajuste soberano». */
const SOVEREIGN_BAND: [number, number] = [0.85, 1.15];

export class ZeroSizeEngine {
  private scan: ScanData;

  constructor(scanData: ScanData) {
    this.scan = { ...scanData };
  }

  calculateSovereignFit(): SovereignFitResult {
    const { chest, shoulder, waist, hip } = this.scan;

    // Ratios normalizados — nunca exponer medidas absolutas en el resultado.
    const hasTorso =
      typeof chest === "number" && chest > 0 &&
      typeof shoulder === "number" && shoulder > 0;

    const hasGirth =
      typeof chest === "number" && chest > 0 &&
      (typeof hip === "number" || typeof waist === "number");

    if (!hasTorso && !hasGirth) {
      return {
        torsoRatio: 0,
        silhouetteIndex: 0,
        fitDescriptor: "insufficient_data",
        patente: PATENTE,
        protocol: PROTOCOL,
      };
    }

    const torsoRatio = hasTorso
      ? (shoulder as number) / Math.max(chest as number, 1e-6)
      : 0;

    const reference = typeof hip === "number" && hip > 0 ? hip : waist ?? 0;
    const silhouetteIndex =
      hasGirth && reference > 0
        ? (chest as number) / reference
        : 0;

    let fitDescriptor: SovereignFitResult["fitDescriptor"];
    if (!hasGirth) {
      fitDescriptor = "insufficient_data";
    } else if (
      silhouetteIndex >= SOVEREIGN_BAND[0] &&
      silhouetteIndex <= SOVEREIGN_BAND[1]
    ) {
      fitDescriptor = "sovereign_fit";
    } else if (silhouetteIndex < SOVEREIGN_BAND[0]) {
      fitDescriptor = "drape_bias";
    } else {
      fitDescriptor = "tension_bias";
    }

    return {
      torsoRatio: Math.round(torsoRatio * 1000) / 1000,
      silhouetteIndex: Math.round(silhouetteIndex * 1000) / 1000,
      fitDescriptor,
      patente: PATENTE,
      protocol: PROTOCOL,
    };
  }
}
