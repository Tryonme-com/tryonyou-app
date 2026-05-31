/**
 * Encadrement UI paiement — EUR / standards européens (pas de USD par défaut).
 */
import type { ReactNode } from "react";
import {
  STRIPE_DEFAULT_COUNTRY,
  STRIPE_DEFAULT_CURRENCY,
} from "../services/stripeParisConfig";

type Props = {
  children?: ReactNode;
  title?: string;
};

export default function PaymentGateway({
  children,
  title = "Paiement sécurisé",
}: Props) {
  return (
    <section
      style={{
        border: "1px solid #D4AF37",
        borderRadius: 4,
        padding: "20px 18px",
        background: "rgba(10,10,10,0.92)",
        color: "#e8e4dc",
        maxWidth: 480,
      }}
    >
      <header style={{ marginBottom: 12 }}>
        <h2
          style={{
            margin: 0,
            fontSize: "1rem",
            letterSpacing: "0.12em",
            color: "#D4AF37",
          }}
        >
          {title}
        </h2>
        <p style={{ margin: "8px 0 0", fontSize: "0.72rem", opacity: 0.8 }}>
          Devise : {STRIPE_DEFAULT_CURRENCY.toUpperCase()} · Pays :{" "}
          {STRIPE_DEFAULT_COUNTRY} · Prestataire : Stripe (compte France vérifié)
        </p>
      </header>
      {children}
    </section>
  );
}
