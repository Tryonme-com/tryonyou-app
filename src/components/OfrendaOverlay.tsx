import type { ReactNode } from "react";

const GOLD = "#C5A46D";

export type OfrendaKey =
  | "selection"
  | "reserve"
  | "combo"
  | "save"
  | "share"
  | "balmain";

const OFRENDA_BOTTOM: { key: OfrendaKey; label: string; accent?: boolean }[] = [
  {
    key: "selection",
    label: "Paiement carte — Non-Stop (sélection parfaite)",
    accent: true,
  },
  { key: "reserve", label: "Reservar en Probador" },
  { key: "combo", label: "Voir les combinaisons" },
  { key: "save", label: "Sac Museum" },
];

type Props = {
  elasticLabel: string;
  julesLane: string;
  onOfrenda: (key: OfrendaKey) => void;
  headerExtra?: ReactNode;
};

export function OfrendaOverlay({
  elasticLabel,
  julesLane,
  onOfrenda,
  headerExtra,
}: Props) {
  return (
    <div className="ofrenda-overlay">
      <div className="ofrenda-header">
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
          Ajustage — {elasticLabel}
        </div>
        {headerExtra}
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

      <div className="ofrenda-spacer" aria-hidden />

      <div>
        <div className="ofrenda-share-row">
          <button
            type="button"
            className="ofrenda-share-btn ofrenda-share-btn--balmain"
            aria-label="Balmain — Espejo Digital"
            onClick={() => onOfrenda("balmain")}
          >
            Balmain
          </button>
          <button
            type="button"
            className="ofrenda-share-btn"
            aria-label="Share My VIP Look"
            onClick={() => onOfrenda("share")}
          >
            Share My VIP Look
          </button>
        </div>
        <div className="ofrenda-bottom-row">
          {OFRENDA_BOTTOM.map((b) => (
            <button
              type="button"
              key={b.key}
              data-accent={b.accent ? "1" : undefined}
              aria-label={`Ofrenda pilote — ${b.label}`}
              onClick={() => onOfrenda(b.key)}
            >
              {b.label}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}

export { OFRENDA_BOTTOM as OFRENDA };
