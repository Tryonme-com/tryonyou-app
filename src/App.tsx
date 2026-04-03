import { useEffect, useState } from "react";
import { OfrendaOverlay, type OfrendaKey } from "./components/OfrendaOverlay";
import { fetchJulesHealth, postMirrorSnap } from "./lib/julesClient";
import "./index.css";
import "./App.css";

function elasticLabelToVerdict(label: string): string {
  if (label.includes("Préférence drapé")) return "drape_bias";
  if (label.includes("Préférence tenue")) return "tension_bias";
  return "aligned";
}

type BunkerSyncResult =
  | { ok: true; data: unknown }
  | { ok: false; error: unknown };

async function syncLeadsToBunker(
  payload: Record<string, unknown>,
): Promise<BunkerSyncResult> {
  try {
    const response = await fetch("/api/vetos_core_inference", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        ...payload,
        system: "BunkerV10_Santuario",
      }),
    });

    const data: Record<string, unknown> = await response.json().catch(() => ({}));

    if (!response.ok) {
      return { ok: false, error: data };
    }

    if (data.status !== "success" || data.leads_synced !== true) {
      return { ok: false, error: data };
    }

    console.log("✅ Sistema Sincronizado:", data);
    return { ok: true, data };
  } catch (error) {
    console.error("❌ Error Crítico Bunker:", error);
    return { ok: false, error };
  }
}

/** Umbral Bpifrance / Mesa: explícito en payload (el API no asume 7500 por defecto). */
const OFRENDA_REVENUE_VALIDATION_EUR = 7500;

async function postLead(intent: OfrendaKey): Promise<void> {
  const payload = {
    intent,
    source: "ofrenda_v10",
    protocol: "zero_size",
    revenue_validation: OFRENDA_REVENUE_VALIDATION_EUR,
  };
  const bunker = await syncLeadsToBunker(payload);
  if (!bunker.ok) {
    console.warn("Bunker sync no completada; no se envía el lead a /api/v1/leads.", bunker.error);
    return;
  }
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

async function postBetaWaitlist(): Promise<void> {
  const email = window.prompt("Email (opcional) para la lista beta:", "") ?? "";
  const payload = {
    email: email.trim() || undefined,
    source: "app_v10",
    user_agent: typeof navigator !== "undefined" ? navigator.userAgent : "",
    ts: new Date().toISOString(),
  };
  try {
    const r = await fetch("/api/waitlist_beta", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    const j = (await r.json().catch(() => ({}))) as {
      waitlist_persisted?: boolean;
      make_ok?: boolean;
    };
    if (!r.ok) {
      window.alert("Lista beta: error de API (revisa consola).");
      return;
    }
    window.alert(
      j.waitlist_persisted
        ? "Inscrito — Make + waitlist (leads_empire/waitlist.json o /tmp en Vercel)."
        : `Webhook Make: ${j.make_ok ? "ok" : "no configurado / fallo"}. Persistencia limitada en serverless.`,
    );
  } catch {
    window.alert("Sin conexión al bunker API.");
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
  const [emailHero, setEmailHero] = useState<string>("");

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

  const onHeroSubmit = async () => {
    const email = emailHero.trim();
    const normalized =
      email.length > 0 ? email : window.prompt("Email para probarla hoy:", "") ?? "";
    const finalEmail = normalized.trim();
    if (!finalEmail) return;
    const payload = {
      email: finalEmail,
      source: "hero_above_the_fold",
      user_agent: typeof navigator !== "undefined" ? navigator.userAgent : "",
      ts: new Date().toISOString(),
    };
    try {
      const r = await fetch("/api/waitlist_beta", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      const j = (await r.json().catch(() => ({}))) as {
        waitlist_persisted?: boolean;
        make_ok?: boolean;
      };
      if (!r.ok) {
        window.alert("No se ha podido registrar tu slot hoy. Prueba en unos minutos.");
        return;
      }
      window.alert(
        j.waitlist_persisted || j.make_ok
          ? "Slot reservado. Te contactaremos para probarla hoy."
          : "Hemos recibido tu solicitud. El bunker te confirmará en breve.",
      );
    } catch {
      window.alert("Sin conexión al bunker API.");
    }
  };

  return (
    <div
      className="app-root"
      style={{
        background: "linear-gradient(145deg, #F5F5DC 0%, #FFFFFF 38%, #D3B26A 100%)",
        color: "#111111",
      }}
    >
      <div className="app-stage" aria-hidden />

      <div className="app-ui">
        <section
          style={{
            padding: "32px 20px 12px",
            maxWidth: 960,
            margin: "0 auto",
          }}
        >
          <p
            style={{
              fontSize: 11,
              letterSpacing: 6,
              textTransform: "uppercase",
              color: "#6b5b3a",
              marginBottom: 10,
            }}
          >
            TRYONYOU · DIVINEO
          </p>
          <p
            style={{
              fontSize: 13,
              letterSpacing: 3,
              textTransform: "uppercase",
              color: "#D3B26A",
              fontStyle: "italic",
              marginBottom: 14,
              marginTop: 0,
            }}
          >
            Essayage Virtuel en France
          </p>
          <h1
            style={{
              fontSize: "clamp(26px, 4vw, 38px)",
              lineHeight: 1.15,
              margin: 0,
              color: "#26201A",
            }}
          >
            Sabrás si te queda bien, antes de comprarlo.
          </h1>
          <p
            style={{
              marginTop: 14,
              maxWidth: 520,
              fontSize: 14,
              lineHeight: 1.7,
              color: "#4a4034",
            }}
          >
            Espejo digital en talla real. Sin probadores crueles, sin tallas que hieren.
            Solo la certeza de verte como eres antes de pagar un solo euro.
          </p>
          <div
            style={{
              display: "flex",
              flexWrap: "wrap",
              gap: 10,
              marginTop: 18,
              alignItems: "center",
            }}
          >
            <input
              type="email"
              value={emailHero}
              onChange={(e) => setEmailHero(e.target.value)}
              placeholder="Tu email para probarla hoy"
              style={{
                flex: "1 1 220px",
                minWidth: 0,
                padding: "10px 14px",
                borderRadius: 999,
                border: "1px solid rgba(0,0,0,0.18)",
                fontSize: 13,
                backgroundColor: "rgba(255,255,255,0.9)",
              }}
            />
            <button
              type="button"
              onClick={onHeroSubmit}
              style={{
                flex: "0 0 auto",
                padding: "11px 22px",
                borderRadius: 999,
                border: "none",
                backgroundColor: "#D3B26A",
                color: "#111111",
                fontSize: 12,
                fontWeight: 600,
                letterSpacing: 2,
                textTransform: "uppercase",
                cursor: "pointer",
                boxShadow: "0 10px 24px rgba(0,0,0,0.12)",
              }}
            >
              Pruébatela YA (5 slots hoy)
            </button>
          </div>
        </section>

        <OfrendaOverlay
          elasticLabel={elasticLabel}
          julesLane={julesLane}
          onOfrenda={onOfrenda}
          headerExtra={
            <button
              type="button"
              onClick={() => void postBetaWaitlist()}
              style={{
                marginTop: 14,
                padding: "8px 18px",
                fontSize: 10,
                letterSpacing: 2,
                textTransform: "uppercase",
                color: "#C5A46D",
                background: "rgba(0,0,0,0.5)",
                border: "1px solid #C5A46D",
                borderRadius: 999,
                cursor: "pointer",
              }}
            >
              Únete a la beta
            </button>
          }
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
