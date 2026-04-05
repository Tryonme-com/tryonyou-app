import React from "react";
import { createRoot } from "react-dom/client";
import "./i18n";
import App from "./App";

/** 🛡️ PROTOCOLO DIVINEO V10.5 - STATUS: CERTEZA ABSOLUTA */
console.log(
  `
%c TRYONYOU | SOUVERAINETÉ 2026 
%c -------------------------------
%c 📂 PROYECTO: gen-lang-client-0091228222
%c 🧬 MESH: 111MB (TRYONYOU1)
%c 🛍️ E-COMMERCE: ZERO-SIZE ACTIVE
%c 🦅 STATUS: PA, PA, PA. BOOM.
`,
  "color: #D4AF37; font-size: 20px; font-weight: bold;",
  "color: #555;",
  "color: #F9FAFB;",
  "color: #CCFF00;",
  "color: #E60000;",
  "color: #D4AF37; font-style: italic;",
);

const el = document.getElementById("root");
if (el) {
  createRoot(el).render(
    <React.StrictMode>
      <App />
    </React.StrictMode>,
  );
}
