import { useCallback, useEffect, useState } from "react";
import { OfrendaOverlay, type OfrendaKey } from "./components/OfrendaOverlay";
import { VirtualMirror } from "./components/VirtualMirror";
import { fetchJulesHealth, postJulesHandshake } from "./lib/julesClient";
import "./index.css";

const GOLD = "#C5A46D";
const ANTHRACITE = "#141619";

async function postLead(intent: OfrendaKey): Promise<void> {
  const payload = {
    intent,
    source: "ofrenda_v10",
    protocol: "zero_size",
  };
  try {
    const r = await fetch("/api/v1/leads", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    if (!r.ok) return;
    void (await r.json());
  } catch {
    /* hors ligne ou préprod */
  }
}

async function postPerfectCheckout(fabricSensation: string): Promise<void> {
  try {
    const r = await fetch("/api/v1/checkout/perfect-selection", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        fabric_sensation: fabricSensation,
        protocol: "zero_size",
      }),
    });
    if (!r.ok) return;
    const j = (await r.json()) as {
      emotional_seal?: string;
      checkout_primary_url?: string;
      checkout_shopify_url?: string;
      checkout_amazon_url?: string;
    };
    if (j.emotional_seal) {
      window.alert(j.emotional_seal);
    }
    const url =
      j.checkout_primary_url ||
      j.checkout_shopify_url ||
      j.checkout_amazon_url;
    if (url) {
      window.open(url, "_blank", "noopener,noreferrer");
    }
  } catch {
    /* silencieux — firewall no rompe UI */
  }
}

export default function App() {
  const [elasticLabel, setElasticLabel] = useState("—");
  const [snapReveal, setSnapReveal] = useState(false);
  const [julesLane, setJulesLane] = useState<string>("Orchestration Jules…");

  useEffect(() => {
    let cancelled = false;
    void (async () => {
      const h = await fetchJulesHealth();
      if (cancelled) return;
      if (h?.ok) {
        setJulesLane(
          `Jules · ${h.service ?? "omega"} · ${h.product_lane ?? "tryonyou_v10_omega"}`,
        );
      } else {
        setJulesLane(
          "Jules · prévisualisation locale (API Python non joignable sur ce port)",
        );
      }
    })();
    return () => {
      cancelled = true;
    };
  }, []);

  const onFitVerdict = useCallback((verdictLabel: string) => {
    setElasticLabel(verdictLabel);
  }, []);

  const onOfrenda = (key: OfrendaKey) => {
    if (key === "selection") {
      void postPerfectCheckout(elasticLabel);
      return;
    }
    void postLead(key);
    const copy: Record<Exclude<OfrendaKey, "selection">, string> = {
      reserve: "QR cabine VIP — Lafayette, essai en courtoisie Divineo.",
      combo: "Lignes alternatives chargées — composition Zero-Size.",
      save: "Silhouette enregistrée sous protocole chiffré (aucune taille exposée).",
      share: "Partage généré — métadonnées d’ajustage neutralisées.",
    };
    if (key !== "selection") {
      window.alert(copy[key]);
    }
  };

  const theSnap = () => {
    void (async () => {
      const j = await postJulesHandshake();
      setSnapReveal(true);
      const msg =
        j?.jules_msg ??
        "The Snap — votre ligne trouve son équilibre. Le drapé répond avec élégance, sans mesure visible.";
      window.alert(msg);
    })();
  };

  return (
    <div className="app-root">
      <VirtualMirror
        revealBalmainSuit={snapReveal}
        onFitVerdict={onFitVerdict}
      />

      <OfrendaOverlay
        elasticLabel={elasticLabel}
        julesLane={julesLane}
        onOfrenda={onOfrenda}
      />

      <button
        type="button"
        onClick={theSnap}
        title="P.A.U."
        aria-label="P.A.U. — snap et orchestration Jules"
        style={{
          position: "fixed",
          bottom: 28,
          left: 28,
          width: 96,
          height: 96,
          borderRadius: "50%",
          border: `2px solid ${GOLD}`,
          overflow: "hidden",
          padding: 0,
          cursor: "pointer",
          zIndex: 60,
          background: ANTHRACITE,
          boxShadow: `0 0 26px rgba(197, 164, 109, 0.35)`,
        }}
      >
        <video
          autoPlay
          loop
          muted
          playsInline
          style={{ width: "100%", height: "100%", objectFit: "cover" }}
        >
          <source src="/pau_transparent.webm" type="video/webm" />
        </video>
      </button>

      <div
        style={{
          position: "fixed",
          bottom: 10,
          width: "100%",
          textAlign: "center",
          fontSize: 8,
          opacity: 0.45,
          letterSpacing: 1,
          pointerEvents: "none",
          zIndex: 40,
        }}
      >
        SIREN: 943 610 196 | Patente: PCT/EP2025/067317 | © 2026 DIVINEO PARIS — V10
        OMEGA
      </div>
    </div>
  );
}
