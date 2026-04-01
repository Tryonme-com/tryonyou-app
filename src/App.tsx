import { lazy, Suspense, useCallback, useEffect, useState } from "react";
import { OfrendaOverlay, type OfrendaKey } from "./components/OfrendaOverlay";
import { fetchJulesHealth, postMirrorSnap } from "./lib/julesClient";
import "./index.css";
import "./App.css";

const VirtualMirror = lazy(() =>
  import("./components/VirtualMirror").then((m) => ({
    default: m.VirtualMirror,
  })),
);

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

function isChasTriggerKey(e: KeyboardEvent): boolean {
  if (e.repeat) return false;
  if (e.code !== "KeyC" || e.ctrlKey || e.metaKey || e.altKey) return false;
  const t = e.target;
  if (!(t instanceof HTMLElement)) return true;
  if (t.tagName === "INPUT" || t.tagName === "TEXTAREA" || t.isContentEditable)
    return false;
  return true;
}

export default function App() {
  const [elasticLabel, setElasticLabel] = useState("—");
  const [lookAugmented, setLookAugmented] = useState(false);
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

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (!isChasTriggerKey(e)) return;
      e.preventDefault();
      setLookAugmented((v) => !v);
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
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
    window.alert(copy[key]);
  };

  const theSnap = () => {
    void (async () => {
      const j = await postMirrorSnap(
        elasticLabel,
        elasticLabelToVerdict(elasticLabel),
      );
      setLookAugmented(true);
      const msg =
        j?.jules_msg ??
        "The Snap — votre ligne trouve son équilibre. Le drapé répond avec élégance, sans mesure visible.";
      window.alert(msg);
    })();
  };

  return (
    <div className="app-root">
      <div className="app-stage">
        <Suspense
          fallback={<div className="loading">LIVIxLAFAYETTE</div>}
        >
          <VirtualMirror
            revealBalmainSuit={lookAugmented}
            onFitVerdict={onFitVerdict}
          />
        </Suspense>
      </div>

      <div className="app-ui">
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
            <video
              autoPlay
              loop
              muted
              playsInline
              preload="auto"
            >
              <source src="/videos/pau_transparent.webm" type="video/webm" />
              <source src="/videos/pau_transparent.mp4" type="video/mp4" />
            </video>
          </button>
        </div>

        <div className="app-legal">
          SIREN: 943 610 196 | Patente: PCT/EP2025/067317 | © 2026 DIVINEO PARIS —
          V10 OMEGA
        </div>
      </div>
    </div>
  );
}
