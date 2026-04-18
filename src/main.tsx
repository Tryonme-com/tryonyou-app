import "./divineo/envBootstrap";
import React from "react";
import { createRoot } from "react-dom/client";
import App from "./App";
import { ParisStripeCheckoutProvider } from "./context/ParisStripeCheckoutContext";

const el = document.getElementById("root");
if (el) {
  createRoot(el).render(
    <React.StrictMode>
      <ParisStripeCheckoutProvider>
        <App />
      </ParisStripeCheckoutProvider>
    </React.StrictMode>,
  );
}
