import { useCallback, useEffect, useState } from "react";
import { OfrendaOverlay, type OfrendaKey } from "./components/OfrendaOverlay";
import { fetchJulesHealth, postMirrorSnap } from "./lib/julesClient";
import { detectLeadScore, type LeadScore } from "./lib/leadScoring";
import "./index.css";
import "./App.css";

function elasticLabelToVerdict(label: string): string {
  if (label.includes("Préférence drapé")) return "drape_bias";
  if (label.includes("Préférence tenue")) return "tension_bias";
  return "aligned";
}

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
    /* hors ligne */
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
        shopping_flow: "non_stop_card",
        anti_accumulation: true,
        single_size_certitude: true,
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
    const primary = j.checkout_primary_url?.trim();
    const shop = j.checkout_shopify_url?.trim();
    const amz = j.checkout_amazon_url?.trim();
    const url = primary || shop || amz;
    if (url) {
      window.open(url, "_blank", "noopener,noreferrer");
    } else if (!j.emotional_seal) {
      window.alert(
        "Parcours enregistré — les ponts marchands seront actifs dès configuration serveur (Zero-Size).",
      );
    }
  } catch {
    /* silencieux */
  }
}

export default function App() {
  const [elasticLabel, setElasticLabel] = useState("—");
  const [julesLane, setJulesLane] = useState<string>("Orchestration Jules…");
  const [leadScore, setLeadScore] = useState<LeadScore>({
    isVip: false,
    brand: null,
    label: "",
  });

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

  useEffect(() => {
    const onFit = (e: Event) => {
      const ce = e as CustomEvent<{ label?: string }>;
      const lab = ce.detail?.label;
      if (typeof lab === "string" && lab.length > 0) setElasticLabel(lab);
    };
    window.addEventListener("tryonyou:fit", onFit);
    return () => window.removeEventListener("tryonyou:fit", onFit);
  }, []);

  // Live Lead Scoring — detect VIP visitors (Inditex / BPI) on mount
  useEffect(() => {
    const score = detectLeadScore();
    if (score.isVip) {
      setLeadScore(score);
      // Apply a subtle VIP colour override via CSS custom properties
      const root = document.documentElement;
      if (score.brand === "inditex") {
        root.style.setProperty("--gold", "#e8c87a");
        root.style.setProperty("--anthracite", "#0d0d14");
      } else if (score.brand === "bpi") {
        root.style.setProperty("--gold", "#7ab8e8");
        root.style.setProperty("--anthracite", "#0a0d14");
      }
      // Notify the backend so the lead is scored in real time
      void fetch("/api/v1/leads", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          intent: "vip_demo",
          source: `lead_scoring_${score.brand}`,
          protocol: "zero_size",
          vip_brand: score.brand,
        }),
      }).catch((err) => { console.warn("[leadScoring] lead POST failed:", err); });
    }
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
    window.alert(copy[key]);
  };

  const theSnap = () => {
    void (async () => {
      const j = await postMirrorSnap(
        elasticLabel,
        elasticLabelToVerdict(elasticLabel),
      );
      const msg =
        j?.jules_msg ??
        "The Snap — votre ligne trouve son équilibre. Le drapé répond avec élégance, sans mesure visible.";
      window.alert(msg);
    })();
  };

  return (
    <div className="app-root">
      <div className="app-stage" aria-hidden />

      <div className="app-ui">
        {leadScore.isVip && (
          <div className="vip-demo-banner" role="status" aria-live="polite">
            <span className="vip-demo-dot" aria-hidden="true" />
            Demo VIP — {leadScore.label}
          </div>
        )}

        <OfrendaOverlay
          elasticLabel={elasticLabel}
          julesLane={julesLane}
          onOfrenda={onOfrenda}
        />

        <div className="app-pau-row">
          <button
            type="button"
            className="app-pau"
            onClick={theSnap}
            title="P.A.U."
            aria-label="P.A.U. — snap et orchestration Jules"
          >
            <video autoPlay loop muted playsInline preload="auto">
              <source src="/videos/pau_transparent.webm" type="video/webm" />
              <source src="/videos/pau_transparent.mp4" type="video/mp4" />
            </video>
          </button>
        </div>
      </div>
    </div>
  );
}
