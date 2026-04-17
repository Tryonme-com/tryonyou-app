/**
 * Terminal de cobro — Protocolo Souveraineté V11 (Rive Gauche verrouillé).
 * No utiliza rutas Next; la SPA completa se sustituye en `main.tsx` cuando la licencia no está activa.
 */

const BG = "#000000";
const GOLD = "#D4AF37";

export default function PaymentTerminal() {
  return (
    <div
      style={{
        minHeight: "100vh",
        background: BG,
        color: GOLD,
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        padding: "32px 24px",
        textAlign: "center",
        fontFamily: 'ui-serif, "Times New Roman", Georgia, serif',
        boxSizing: "border-box",
      }}
    >
      <div
        style={{
          maxWidth: 640,
          border: `1px solid ${GOLD}`,
          padding: "48px 36px",
          boxShadow: `0 0 40px rgba(212, 175, 55, 0.15)`,
        }}
      >
        <h1
          style={{
            margin: 0,
            fontSize: "clamp(1.15rem, 3.5vw, 1.65rem)",
            letterSpacing: "0.35em",
            fontWeight: 600,
            lineHeight: 1.4,
          }}
        >
          ACCÈS RÉSERVÉ : LICENCE SOUVERAINETÉ V11
        </h1>
        <p
          style={{
            marginTop: 28,
            fontSize: "1rem",
            lineHeight: 1.7,
            opacity: 0.92,
            letterSpacing: "0.06em",
          }}
        >
          Le salon Le Bon Marché Rive Gauche est verrouillé pour défaut de paiement de
          licence.
        </p>
        <p
          style={{
            marginTop: 36,
            fontSize: "clamp(1.75rem, 5vw, 2.75rem)",
            fontWeight: 600,
            letterSpacing: "0.12em",
          }}
        >
          109.900,00 €
        </p>
        <a
          href="tel:+33699469479"
          style={{
            display: "inline-block",
            marginTop: 40,
            padding: "16px 28px",
            background: "transparent",
            color: GOLD,
            border: `2px solid ${GOLD}`,
            textDecoration: "none",
            fontSize: "0.72rem",
            letterSpacing: "0.2em",
            fontWeight: 600,
          }}
        >
          CONTACTER RUBÉN ESPINAR : +33 6 99 46 94 79
        </a>
        <p
          style={{
            marginTop: 32,
            fontSize: "0.65rem",
            letterSpacing: "0.15em",
            opacity: 0.55,
          }}
        >
          SIREN 943 610 196 · PCT/EP2025/067317 · DIVINEO PARIS
        </p>
      </div>
    </div>
  );
}
