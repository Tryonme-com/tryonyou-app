import "./divineo/envBootstrap";
import "./lib/empire_final_protocol.js";
import React from "react";
import { createRoot } from "react-dom/client";
import App from "./App";
import { ParisStripeCheckoutProvider } from "./context/ParisStripeCheckoutContext";

const el = document.getElementById("root") as HTMLDivElement | null;
if (el) {
  createRoot(el).render(
    <React.StrictMode>
      <ParisStripeCheckoutProvider>
        <App />
      </ParisStripeCheckoutProvider>
    </React.StrictMode>,
  );
}
