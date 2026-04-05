/** 🛡️ INTERFAZ DE EJECUCIÓN V1.0
 * UBICACIÓN: tryonyou-app-ruben-espinar-rodriguez-pro.vercel.app
 * OBJETIVO: Pasar de 'Pitch Deck' a 'Producto Real'.
 */

import { useState } from "react";
import { initializeHolisticEngine } from "../engines/RobertEngine";

const GOLD = "#D4AF37";

export const LiveDemo = () => {
  const [isLive, setIsLive] = useState(false);

  const startSovereignScan = () => {
    setIsLive(true);
    console.log("PA, PA, PA - ACTIVANDO CERTEZA BIOMÉTRICA...");
    initializeHolisticEngine();
  };

  return (
    <div
      style={{
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        gap: 12,
        padding: "20px",
      }}
    >
      {!isLive ? (
        <button
          type="button"
          onClick={startSovereignScan}
          style={{
            padding: "14px 32px",
            borderRadius: 999,
            border: `1px solid ${GOLD}`,
            background: "transparent",
            color: GOLD,
            fontSize: 11,
            fontWeight: 700,
            letterSpacing: 4,
            textTransform: "uppercase",
            cursor: "pointer",
            transition: "background 0.2s ease",
          }}
          onMouseEnter={(e) => {
            (e.currentTarget as HTMLButtonElement).style.background =
              "rgba(212,175,55,0.12)";
          }}
          onMouseLeave={(e) => {
            (e.currentTarget as HTMLButtonElement).style.background = "transparent";
          }}
        >
          ACTIVAR CERTEZA BIOMÉTRICA
        </button>
      ) : (
        <div
          style={{
            fontSize: 10,
            letterSpacing: 3,
            textTransform: "uppercase",
            color: GOLD,
            padding: "8px 18px",
            border: `1px solid ${GOLD}`,
            borderRadius: 999,
            background: "rgba(0,0,0,0.35)",
          }}
        >
          ● SISTEMA EN VIVO
        </div>
      )}
      <p
        style={{
          fontSize: 9,
          color: "#555",
          letterSpacing: 2,
          textTransform: "uppercase",
          margin: 0,
          textAlign: "center",
        }}
      >
        TRYONYOU · CERTEZA BIOMÉTRICA · ZERO-SIZE
      </p>
    </div>
  );
};
