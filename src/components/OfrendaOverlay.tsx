import type { ReactNode } from "react";

const GOLD = "#C5A46D";

export type OfrendaKey =
  | "selection"
  | "reserve"
  | "combo"
  | "save"
  | "share";

const OFRENDA: { key: OfrendaKey; label: string }[] = [
  { key: "selection", label: "Ma sélection parfaite" },
  { key: "reserve", label: "Réserver cabine" },
  { key: "combo", label: "Voir les combinaisons" },
  { key: "save", label: "Enregistrer ma silhouette" },
  { key: "share", label: "Partager le look (mode Zero-Size)" },
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
  );
}

export { OFRENDA };
