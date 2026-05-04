/**
 * MirrorBlackScreenQR — overlay affiché en plein écran quand le miroir physique
 * est en mode Black-Screen (mirrorPoweredOn === false).
 *
 * Affiche le QR de liquidation pour que l'opérateur du salon puisse scanner et
 * régulariser le paiement de licence directement depuis l'écran du miroir.
 *
 * Protocolo Souveraineté V11 — Rubén Espinar · DIVINEO PARIS · PCT/EP2025/067317
 */

import { QRCodeSVG } from "qrcode.react";

const BG = "#000000";
const GOLD = "#D4AF37";
const GOLD_DIM = "rgba(212,175,55,0.45)";

type Props = {
  settlementUrl: string;
  /** Montant affiché sous le QR (ex. "109.900,00 €"). */
  amount?: string;
};

export default function MirrorBlackScreenQR({
  settlementUrl,
  amount = "109.900,00 €",
}: Props) {
  const url = settlementUrl.trim() || "https://tryonme.com";

  return (
    <div
      role="dialog"
      aria-label="Miroir suspendu — QR de liquidation"
      style={{
        position: "fixed",
        inset: 0,
        zIndex: 9999,
        background: BG,
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        gap: 32,
        padding: "48px 24px",
        textAlign: "center",
        fontFamily: 'ui-serif, "Times New Roman", Georgia, serif',
      }}
    >
      {/* Scan line animée */}
      <div
        aria-hidden="true"
        style={{
          position: "absolute",
          inset: 0,
          overflow: "hidden",
          pointerEvents: "none",
        }}
      >
        <div className="mirror-scan" />
      </div>

      <p
        style={{
          margin: 0,
          fontSize: "clamp(0.55rem, 1.5vw, 0.75rem)",
          letterSpacing: "0.35em",
          textTransform: "uppercase",
          color: GOLD_DIM,
        }}
      >
        TRYONME × DIVINEO
      </p>

      <h1
        style={{
          margin: 0,
          fontSize: "clamp(0.9rem, 2.5vw, 1.3rem)",
          letterSpacing: "0.3em",
          fontWeight: 500,
          color: GOLD,
          lineHeight: 1.4,
        }}
      >
        MIROIR SUSPENDU
      </h1>

      {/* QR code encadré */}
      <div
        style={{
          padding: 20,
          border: `1px solid ${GOLD}`,
          background: "#fff",
          boxShadow: `0 0 40px rgba(212,175,55,0.25)`,
          display: "inline-flex",
        }}
      >
        <QRCodeSVG
          value={url}
          size={220}
          bgColor="#ffffff"
          fgColor="#000000"
          level="M"
          aria-label="QR de liquidation"
        />
      </div>

      {/* Montant */}
      <p
        style={{
          margin: 0,
          fontSize: "clamp(1.6rem, 4.5vw, 2.5rem)",
          fontWeight: 600,
          letterSpacing: "0.12em",
          color: GOLD,
        }}
      >
        {amount}
      </p>

      <p
        style={{
          margin: 0,
          fontSize: "clamp(0.65rem, 1.8vw, 0.85rem)",
          letterSpacing: "0.2em",
          textTransform: "uppercase",
          color: GOLD,
          opacity: 0.88,
        }}
      >
        SCANNER POUR RÉACTIVER LE MIROIR
      </p>

      <p
        style={{
          margin: 0,
          fontSize: "0.58rem",
          letterSpacing: "0.15em",
          opacity: 0.45,
          color: GOLD,
          textTransform: "uppercase",
        }}
      >
        SIREN 943 610 196 · PCT/EP2025/067317 · DIVINEO PARIS
      </p>
    </div>
  );
}
