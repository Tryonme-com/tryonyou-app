import { useCallback, useEffect, useState } from "react";
import { VirtualMirror } from "./components/VirtualMirror";
import { fetchJulesHealth, postJulesHandshake } from "./lib/julesClient";
import "./index.css";

const GOLD = "#C5A46D";
const ANTHRACITE = "#141619";

type OfrendaKey = "selection" | "reserve" | "combo" | "save" | "share";

const OFRENDA: { key: OfrendaKey; label: string }[] = [
  { key: "selection", label: "Ma sélection parfaite" },
  { key: "reserve", label: "Réserver cabine" },
  { key: "combo", label: "Voir les combinaisons" },
  { key: "save", label: "Enregistrer ma silhouette" },
  { key: "share", label: "Partager le look (mode Zero-Size)" },
];

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
    const _j = await r.json();
    void _j;
  } catch {
    /* hors ligne ou préprod */
  }
}

export default function App() {
  const [elasticLabel, setElasticLabel] = useState("—");
  const [ema, setEma] = useState<number | null>(null);
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

  const onElasticity = useCallback((_ema: number, verdictLabel: string) => {
    setEma(_ema);
    setElasticLabel(verdictLabel);
  }, []);

  const onOfrenda = (key: OfrendaKey) => {
    void postLead(key);
    const copy: Record<OfrendaKey, string> = {
      selection:
        "Analyse d’épaule et drape en cours — envoyé au parcours d’essayage.",
      reserve: "QR cabine VIP généré — Lafayette (référence pilote).",
      combo: "Alternatives de ligne Divineo chargées.",
      save: "Empreinte silhouette chiffrée (Zero-Size).",
      share: "Visuel généré — métadonnées d’ajustage neutralisées.",
    };
    alert(copy[key]);
  };

  const theSnap = () => {
    void (async () => {
      const j = await postJulesHandshake();
      const msg =
        j?.jules_msg ??
        "The Snap : élasticité et cohérence drape — look de référence pilote.";
      alert(msg);
    })();
  };

  return (
    <div className="app-root">
      <VirtualMirror onElasticity={onElasticity} />

      <div
        style={{
          position: "absolute",
          inset: 0,
          display: "flex",
          flexDirection: "column",
          justifyContent: "space-between",
          padding: "36px 20px 100px",
          pointerEvents: "none",
          zIndex: 50,
        }}
      >
        <div style={{ textAlign: "center" }}>
          <h1
            style={{
              margin: 0,
              letterSpacing: 10,
              fontSize: 22,
              textShadow: `0 0 18px rgba(197, 164, 109, 0.45)`,
            }}
          >
            TRYONYOU
          </h1>
          <div
            style={{
              marginTop: 10,
              fontSize: 10,
              letterSpacing: 2,
              color: GOLD,
              border: `1px solid ${GOLD}`,
              display: "inline-block",
              padding: "6px 14px",
              borderRadius: 999,
              background: "rgba(0,0,0,0.35)",
            }}
          >
            Elasticité (EMA) · {ema != null ? ema.toFixed(3) : "…"} ·{" "}
            {elasticLabel}
          </div>
          <p
            style={{
              margin: "12px 0 0",
              fontSize: 9,
              letterSpacing: 1,
              opacity: 0.75,
              maxWidth: 480,
              marginLeft: "auto",
              marginRight: "auto",
              lineHeight: 1.5,
            }}
          >
            {julesLane}
          </p>
        </div>

        <div
          style={{
            pointerEvents: "auto",
            display: "grid",
            gridTemplateColumns: "1fr 1fr",
            gap: 12,
            maxWidth: 520,
            width: "100%",
            alignSelf: "center",
          }}
        >
          {OFRENDA.map((b, i) => (
            <button
              type="button"
              key={b.key}
              aria-label={`Ofrenda pilote — ${b.label}`}
              onClick={() => onOfrenda(b.key)}
              style={{
                gridColumn: i === 4 ? "span 2" : undefined,
                padding: "16px 10px",
                fontSize: 10,
                letterSpacing: 2,
                textTransform: "uppercase",
                color: GOLD,
                border: `1px solid ${GOLD}`,
                background:
                  i === 4 ? "rgba(197, 164, 109, 0.14)" : "var(--glass)",
                backdropFilter: "blur(12px)",
                cursor: "pointer",
                borderRadius: 4,
                fontFamily: "inherit",
                transition: "transform 0.2s, background 0.2s",
              }}
            >
              {b.label}
            </button>
          ))}
        </div>
      </div>

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
