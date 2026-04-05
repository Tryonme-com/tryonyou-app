import { useEffect, useState } from "react";
import { createPerfectCheckout } from "./shopifyCheckout.js";

function App() {
  const [elasticLabel, setElasticLabel] = useState("Analyse en cours…");
  const [snapDone, setSnapDone] = useState(false);
  const [biometricHash, setBiometricHash] = useState("");

  useEffect(() => {
    const onFit = (e) => {
      const label = e.detail?.label;
      if (typeof label === "string" && label.length > 0) {
        setElasticLabel(label);
      }
      const hash = e.detail?.biometricHash;
      if (typeof hash === "string" && hash.length > 0) {
        setBiometricHash(hash);
      }
    };
    window.addEventListener("tryonyou:fit", onFit);
    return () => window.removeEventListener("tryonyou:fit", onFit);
  }, []);

  const handleSnap = () => {
    setSnapDone(true);
    const hash = biometricHash || `tryonyou-${Date.now()}`;
    createPerfectCheckout(hash);
    setTimeout(() => setSnapDone(false), 2000);
  };

  return (
    <div
      style={{
        position: "fixed",
        inset: 0,
        display: "flex",
        flexDirection: "column",
        justifyContent: "flex-end",
        pointerEvents: "none",
        zIndex: 50,
      }}
    >
      <div
        style={{
          pointerEvents: "auto",
          background: "rgba(0,0,0,0.75)",
          backdropFilter: "blur(12px)",
          padding: "20px 24px",
          borderTop: "1px solid rgba(212,175,55,0.3)",
          display: "flex",
          flexDirection: "column",
          gap: 12,
        }}
      >
        <div
          style={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
          }}
        >
          <span
            style={{
              fontSize: 10,
              letterSpacing: 3,
              textTransform: "uppercase",
              color: "#D4AF37",
            }}
          >
            ESPEJO DIVINEO V100
          </span>
          <span
            style={{
              fontSize: 11,
              color: "#aaa",
              fontStyle: "italic",
            }}
          >
            {elasticLabel}
          </span>
        </div>

        <button
          type="button"
          onClick={handleSnap}
          style={{
            background: snapDone
              ? "#4caf50"
              : "linear-gradient(135deg, #D4AF37 0%, #b8942e 100%)",
            color: "#000",
            border: "none",
            borderRadius: 999,
            padding: "14px 32px",
            fontSize: 11,
            fontWeight: 700,
            letterSpacing: 4,
            textTransform: "uppercase",
            cursor: "pointer",
            transition: "background 0.3s ease",
            boxShadow: "0 8px 24px rgba(212,175,55,0.35)",
          }}
        >
          {snapDone ? "✓ SNAP CAPTURADO" : "THE SNAP — DIVINEO"}
        </button>

        <p
          style={{
            fontSize: 9,
            color: "#555",
            textAlign: "center",
            letterSpacing: 2,
            textTransform: "uppercase",
            margin: 0,
          }}
        >
          TRYONYOU V100 · ZERO-SIZE · PCT/EP2025/067317
        </p>
      </div>
    </div>
  );
}

export default App;
