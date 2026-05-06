import "./divineo/envBootstrap";
import "./lib/empire_final_protocol.js";
import React from "react";
import { createRoot } from "react-dom/client";
import App from "./App";
import { ParisStripeCheckoutProvider } from "./context/ParisStripeCheckoutContext";
import { isSovereigntyLicenseActive } from "./lib/licenseGate";
import PaymentTerminal from "./pages/payment-terminal";

const el = document.getElementById("root") as HTMLDivElement | null;
if (el) {
  const path = window.location.pathname;
  const isPaymentTerminal =
    path === "/payment-terminal" || path.startsWith("/payment-terminal/");
  const shouldShowPaymentTerminal = isPaymentTerminal || !isSovereigntyLicenseActive();

  createRoot(el).render(
    <React.StrictMode>
      {shouldShowPaymentTerminal ? (
        <PaymentTerminal />
      ) : (
        <ParisStripeCheckoutProvider>
          <App />
        </ParisStripeCheckoutProvider>
      )}
    </React.StrictMode>,
  );
}
