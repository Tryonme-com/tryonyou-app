/**
 * FrictionToFlowOverlay — interface "Friction-to-Flow" affichée sur les miroirs physiques
 * après un scan de silhouette réussi (theSnap).
 *
 * Élimine la friction de taille en présentant immédiatement un QR de passage en caisse
 * que le client scanne avec son téléphone. Le drapé s'achète en un geste — Zero-Size.
 *
 * Protocolo Souveraineté V11 — Rubén Espinar · DIVINEO PARIS · PCT/EP2025/067317
 */

import { useEffect, useState } from "react";
import { QRCodeSVG } from "qrcode.react";

const BG_OVERLAY = "rgba(5,5,8,0.93)";
const GOLD = "#D4AF37";

/** Durée d'affichage automatique (ms) avant fermeture silencieuse. */
const AUTO_DISMISS_MS = 18_000;

type Props = {
  /** URL de passage en caisse (Stripe / abvetos.com). */
  checkoutUrl: string;
  /** Message Jules issu du snap (jules_msg). */
  julesMsg?: string;
  /** Étiquette d'ajustage Elastic actuelle (ex. "Préférence drapé"). */
  elasticLabel?: string;
  /** Callback de fermeture. */
  onClose: () => void;
};

export default function FrictionToFlowOverlay({
  checkoutUrl,
  julesMsg,
  elasticLabel,
  onClose,
}: Props) {
  const [secondsLeft, setSecondsLeft] = useState(
    Math.round(AUTO_DISMISS_MS / 1000),
  );

  /* Auto-dismiss avec compte à rebours. */
  useEffect(() => {
    const tick = window.setInterval(() => {
      setSecondsLeft((s) => {
        if (s <= 1) {
          clearInterval(tick);
          onClose();
          return 0;
        }
        return s - 1;
      });
    }, 1000);
    return () => clearInterval(tick);
  }, [onClose]);

  const url = checkoutUrl.trim() || "https://tryonme.com";

  return (
    <div
      role="dialog"
      aria-modal="true"
      aria-label="Friction-to-Flow — scanner pour finaliser"
      onClick={onClose}
      style={{
        position: "fixed",
        inset: 0,
        zIndex: 9500,
        background: BG_OVERLAY,
        backdropFilter: "blur(18px)",
        WebkitBackdropFilter: "blur(18px)",
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        gap: 28,
        padding: "48px 24px",
        textAlign: "center",
        fontFamily: 'ui-serif, "Times New Roman", Georgia, serif',
        cursor: "pointer",
      }}
    >
      {/* Scan line animée */}
      <div
        aria-hidden="true"
        style={{ position: "absolute", inset: 0, overflow: "hidden", pointerEvents: "none" }}
      >
        <div className="mirror-scan" />
      </div>

      {/* En-tête */}
      <div style={{ display: "flex", flexDirection: "column", gap: 6, position: "relative" }}>
        <p
          style={{
            margin: 0,
            fontSize: "clamp(0.55rem, 1.4vw, 0.72rem)",
            letterSpacing: "0.4em",
            textTransform: "uppercase",
            color: "rgba(212,175,55,0.6)",
          }}
        >
          FRICTION-TO-FLOW
        </p>
        <h2
          style={{
            margin: 0,
            fontSize: "clamp(1.1rem, 3vw, 1.8rem)",
            fontWeight: 500,
            letterSpacing: "0.22em",
            color: GOLD,
            lineHeight: 1.35,
          }}
        >
          VOTRE TENUE EST PRÊTE
        </h2>
        {elasticLabel ? (
          <p
            style={{
              margin: 0,
              fontSize: "clamp(0.65rem, 1.6vw, 0.82rem)",
              letterSpacing: "0.18em",
              color: "rgba(212,175,55,0.82)",
              fontStyle: "italic",
            }}
          >
            {elasticLabel}
          </p>
        ) : null}
      </div>

      {/* QR code encadré */}
      <div
        onClick={(e) => e.stopPropagation()}
        style={{
          padding: 18,
          border: `1px solid ${GOLD}`,
          background: "#fff",
          boxShadow: `0 0 50px rgba(212,175,55,0.3)`,
          display: "inline-flex",
          position: "relative",
        }}
      >
        <QRCodeSVG
          value={url}
          size={240}
          bgColor="#ffffff"
          fgColor="#000000"
          level="M"
          aria-label="QR code checkout"
        />
      </div>

      {/* CTA scan */}
      <p
        style={{
          margin: 0,
          fontSize: "clamp(0.75rem, 2vw, 1rem)",
          letterSpacing: "0.28em",
          textTransform: "uppercase",
          color: GOLD,
          fontWeight: 500,
        }}
      >
        SCANNER &amp; FINALISER
      </p>

      {/* Message Jules */}
      {julesMsg ? (
        <p
          style={{
            margin: 0,
            maxWidth: 520,
            fontSize: "clamp(0.68rem, 1.6vw, 0.82rem)",
            lineHeight: 1.65,
            letterSpacing: "0.05em",
            color: "rgba(236,228,216,0.78)",
            fontStyle: "italic",
          }}
        >
          {julesMsg}
        </p>
      ) : null}

      {/* Compte à rebours */}
      <p
        aria-live="polite"
        style={{
          margin: 0,
          fontSize: "0.6rem",
          letterSpacing: "0.2em",
          textTransform: "uppercase",
          color: "rgba(212,175,55,0.45)",
        }}
      >
        FERMETURE AUTOMATIQUE · {secondsLeft}s · APPUYER POUR FERMER
      </p>
    </div>
  );
}
