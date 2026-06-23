import React, { useState, useCallback } from "react";

const GOLD = "#C5A46D";
const GOLD_BORDER = "1px solid #C5A46D";
const BG_DARK = "rgba(0, 0, 0, 0.70)";
const BG_DARKER = "rgba(0, 0, 0, 0.85)";

export type SupportedLanguage = "fr" | "en" | "es";

export type OfrendaKey =
  | "selection"
  | "reserve"
  | "combo"
  | "save"
  | "share"
  | "balmain";

export interface OfrendaMetadata {
  timestamp: string;
  qrCode?: string;
  status?: string;
  savedProfile?: boolean;
  imageDataUrl?: string;
  captureError?: string;
}

const TRANSLATIONS: Record<SupportedLanguage, Record<string, string>> = {
  fr: {
    title:     "TRYONYOU",
    adjustment: "Ajustage",
    selection: "Paiement carte — Non-Stop (Sélection Parfaite)",
    reserve:   "Réserver en Cabine",
    combo:     "Voir les Combinaisons",
    save:      "Sauvegarder ma Silhouette",
    share:     "Partager Mon Look VIP",
    balmain:   "Balmain",
  },
  en: {
    title:     "TRYONYOU",
    adjustment: "Adjustment",
    selection: "Card Payment — Non-Stop (Perfect Selection)",
    reserve:   "Reserve in Fitting Room",
    combo:     "View Combinations",
    save:      "Save My Silhouette",
    share:     "Share My VIP Look",
    balmain:   "Balmain",
  },
  es: {
    title:     "TRYONYOU",
    adjustment: "Ajuste",
    selection: "Pago con tarjeta — Non-Stop (Selección Perfecta)",
    reserve:   "Reservar en Probador",
    combo:     "Ver Combinaciones",
    save:      "Guardar mi Silueta",
    share:     "Compartir mi Look VIP",
    balmain:   "Balmain",
  },
};

export interface OfrendaOverlayProps {
  elasticLabel: string;
  julesLane: string;
  onOfrenda: (key: OfrendaKey, metadata: OfrendaMetadata) => void;
  headerExtra?: React.ReactNode;
  initialLang?: SupportedLanguage;
  canvasRef?: React.RefObject<HTMLCanvasElement>;
}

export function OfrendaOverlay({
  elasticLabel,
  julesLane,
  onOfrenda,
  headerExtra,
  initialLang = "fr",
  canvasRef,
}: OfrendaOverlayProps) {
  const [lang, setLang] = useState<SupportedLanguage>(initialLang);
  const t = TRANSLATIONS[lang];

  const handleAction = useCallback(
    (key: OfrendaKey) => {
      const base: OfrendaMetadata = { timestamp: new Date().toISOString() };

      switch (key) {
        case "reserve":
          base.qrCode = "QR-TRYON-" + Date.now();
          base.status = "RESERVED_IN_STORE";
          break;
        case "save":
          base.savedProfile = True;
          break;
        case "share": {
          const canvas = canvasRef?.current ?? (document.querySelector("canvas") as HTMLCanvasElement | null);
          if (canvas) {
            try {
              base.imageDataUrl = canvas.toDataURL("image/png");
            } catch {
              base.captureError = "Canvas tainted — cross-origin media detected";
            }
          } else {
            base.captureError = "No canvas element found in the document";
          }
          break;
        }
        default:
          break;
      }
      onOfrenda(key, base);
    },
    [canvasRef, onOfrenda]
  );

  const primaryBtnStyle: React.CSSProperties = {
    padding: "12px 24px",
    background: GOLD,
    color: "#000",
    border: "none",
    fontWeight: "bold",
    cursor: "pointer",
    fontSize: 11,
    letterSpacing: 1,
    textTransform: "uppercase",
  };

  const secondaryBtnStyle: React.CSSProperties = {
    padding: "12px 24px",
    background: BG_DARK,
    color: "#FFF",
    border: "1px solid #FFF",
    cursor: "pointer",
    fontSize: 11,
    letterSpacing: 1,
    textTransform: "uppercase",
  };

  const brandBtnStyle: React.CSSProperties = {
    padding: "10px 20px",
    background: BG_DARKER,
    border: GOLD_BORDER,
    color: GOLD,
    letterSpacing: 2,
    cursor: "pointer",
    textTransform: "uppercase",
    fontSize: 11,
  };

  const shareBtnStyle: React.CSSProperties = {
    padding: "10px 20px",
    background: BG_DARKER,
    border: GOLD_BORDER,
    color: "#FFF",
    letterSpacing: 1,
    cursor: "pointer",
    fontSize: 11,
    textTransform: "uppercase",
  };

  return (
    <div
      className="ofrenda-overlay"
      style={{
        fontFamily: "system-ui, -apple-system, sans-serif",
        color: "#F5F5F5",
        position: "relative",
        width: "100%",
        height: "100%",
        pointerEvents: "none",
      }}
    >
      <div style={{ position: "absolute", top: 20, right: 20, display: "flex", gap: 8, zIndex: 10, pointerEvents: "auto" }}>
        {(["fr", "en", "es"] as SupportedLanguage[]).map((l) => (
          <button
            key={l}
            onClick={() => setLang(l)}
            aria-pressed={lang === l}
            style={{
              background: lang === l ? GOLD : "rgba(0,0,0,0.5)",
              color: lang === l ? "#000" : "#FFF",
              border: GOLD_BORDER,
              padding: "4px 8px",
              cursor: "pointer",
              fontSize: 10,
              textTransform: "uppercase",
              fontWeight: lang === l ? "bold" : "normal",
            }}
          >
            {l.toUpperCase()}
          </button>
        ))}
      </div>

      <div style={{ textAlign: "center", paddingTop: 40 }}>
        <h1 style={{ margin: 0, letterSpacing: 10, fontSize: 22, fontWeight: 300, textShadow: "0 0 18px rgba(197, 164, 109, 0.45)" }}>
          {t.title}
        </h1>
        <div style={{ marginTop: 10, fontSize: 10, letterSpacing: 2, color: GOLD, border: GOLD_BORDER, display: "inline-block", padding: "6px 14px", borderRadius: 999, background: "rgba(0,0,0,0.35)", backdropFilter: "blur(4px)" }}>
          {t.adjustment} — {elasticLabel}
        </div>
        {headerExtra}
        <p style={{ margin: "12px auto 0", fontSize: 9, letterSpacing: 1, opacity: 0.75, maxWidth: 480, lineHeight: 1.5 }}>
          {julesLane}
        </p>
      </div>

      <div aria-hidden style={{ height: "35vh" }} />

      <div style={{ padding: "20px", display: "flex", flexDirection: "column", gap: "12px", pointerEvents: "auto" }}>
        <div style={{ display: "flex", gap: "10px", justifyContent: "center", flexWrap: "wrap" }}>
          <button type="button" style={brandBtnStyle} onClick={() => handleAction("balmain")} aria-label="Switch to Balmain garment collection">
            {t.balmain}
          </button>
          <button type="button" style={shareBtnStyle} onClick={() => handleAction("share")} aria-label={t.share}>
            {t.share}
          </button>
        </div>

        <div style={{ display: "flex", flexWrap: "wrap", gap: "10px", justifyContent: "center" }}>
          <button type="button" style={primaryBtnStyle} onClick={() => handleAction("selection")} aria-label={t.selection}>
            {t.selection}
          </button>
          <button type="button" style={secondaryBtnStyle} onClick={() => handleAction("reserve")} aria-label={t.reserve}>
            {t.reserve}
          </button>
          <button type="button" style={secondaryBtnStyle} onClick={() => handleAction("combo")} aria-label={t.combo}>
            {t.combo}
          </button>
          <button type="button" style={secondaryBtnStyle} onClick={() => handleAction("save")} aria-label={t.save}>
            {t.save}
          </button>
        </div>
      </div>
    </div>
  );
}
