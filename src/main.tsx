import React from "react";
import { createRoot } from "react-dom/client";
import App from "./App";
import { PaymentTerminal } from "./components/PaymentTerminal";

const isPaid = import.meta.env.VITE_LICENSE_PAID === "true";
const RootComponent = isPaid ? App : PaymentTerminal;

const el = document.getElementById("root");
if (el) {
  createRoot(el).render(
    <React.StrictMode>
      <RootComponent />
    </React.StrictMode>,
  );
}
