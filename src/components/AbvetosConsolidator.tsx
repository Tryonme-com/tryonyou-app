/**
 * Consolidateur abvetos — l’Architecte ne déclenche que la pasarela Stripe Paris (EUR).
 */
import { useState } from "react";
import PaymentGateway from "./PaymentGateway";
import { useParisStripeCheckout } from "../context/ParisStripeCheckoutContext";
import { getInaugurationStripeCheckoutUrl } from "../lib/lafayetteCheckout";
import { architectOpenVerifiedParisCheckout } from "../services/paymentService";

export default function AbvetosConsolidator() {
  const { checkoutApiReady, checkoutProbeError } = useParisStripeCheckout();
  const hasStaticCheckout = Boolean(getInaugurationStripeCheckoutUrl().trim());
  const [pending, setPending] = useState(false);
  const [err, setErr] = useState<string | null>(null);

  const onPay = async () => {
    setErr(null);
    setPending(true);
    try {
      const ok = await architectOpenVerifiedParisCheckout();
      if (!ok) {
        setErr(
          "Configurez VITE_INAUGURATION_STRIPE_CHECKOUT_URL ou l’API /api/stripe_inauguration_checkout (compte France).",
        );
      }
    } finally {
      setPending(false);
    }
  };

  return (
    <PaymentGateway title="L’Architecte · pasarela vérifiée (Paris)">
      <p style={{ margin: "0 0 16px", fontSize: "0.8rem", lineHeight: 1.55 }}>
        Les ordres de paiement sont routés vers le compte Stripe France vérifié (EUR). Aucun
        encaissement par défaut vers un compte américain non vérifié.
      </p>
      {!hasStaticCheckout && !checkoutApiReady ? (
        <p style={{ margin: "0 0 12px", fontSize: "0.68rem", color: "#8a7a5c" }}>
          Vérification du compte Stripe Paris (session)…
        </p>
      ) : null}
      {checkoutProbeError && !hasStaticCheckout ? (
        <p style={{ margin: "0 0 12px", fontSize: "0.68rem", color: "#a8842c" }}>
          Session Stripe indisponible pour l’instant — vérifiez l’API ou l’URL statique.
        </p>
      ) : null}
      <button
        type="button"
        disabled={pending || (!hasStaticCheckout && !checkoutApiReady)}
        onClick={() => void onPay()}
        style={{
          width: "100%",
          padding: "12px 16px",
          background: "#1a1510",
          color: "#D4AF37",
          border: "1px solid #D4AF37",
          borderRadius: 4,
          fontSize: "0.72rem",
          letterSpacing: "0.14em",
          cursor: pending ? "wait" : "pointer",
        }}
      >
        {pending ? "CONNEXION STRIPE PARIS…" : "OUVRIR LE PAIEMENT (EUR)"}
      </button>
      {err ? (
        <p style={{ margin: "12px 0 0", fontSize: "0.7rem", color: "#c9a227" }}>{err}</p>
      ) : null}
    </PaymentGateway>
  );
}
