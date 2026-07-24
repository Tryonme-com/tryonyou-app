import "./divineo/envBootstrap";
import React from "react";
import { createRoot } from "react-dom/client";
import App from "./App";
import { startMediapipeFitBridge } from "./bootstrap/mediapipeFitBridge";
import { applySovereignLockdownIfNeeded } from "./bootstrap/sovereignLockdown";

applySovereignLockdownIfNeeded();

const el = document.getElementById("root");
if (el) {
  createRoot(el).render(
    <React.StrictMode>
      <App />
    </React.StrictMode>,
  );
}

let stopBridge: () => void = () => undefined;
void startMediapipeFitBridge()
  .then((cleanup) => {
    stopBridge = cleanup;
  })
  .catch(() => {
    /* fail silent: App conserva etiqueta V9 por defecto */
  });

window.addEventListener(
  "beforeunload",
  () => {
    stopBridge();
  },
  { once: true },
);
