/**
 * CollaboratorNav — barra de navegación por tipo de colaborador.
 *
 * Reemplaza la inyección HTML de collaborator_bridge.py con un componente
 * React reutilizable que llama al endpoint /api/v1/collaborators/filter.
 */

const GOLD = "#D4AF37";
const DARK = "#1a1a1a";
const NAV_BOTTOM_OFFSET = 100;
const NAV_GAP = 20;
const BTN_FONT_SIZE = "0.75rem";

export type CollaboratorType =
  | "ARMARIO SOLIDARIO"
  | "ARMARIO INTELIGENTE"
  | "SAC MUSEUM";

type CollaboratorButton = {
  type: CollaboratorType;
  label: string;
  style: React.CSSProperties;
};

const BUTTONS: CollaboratorButton[] = [
  {
    type: "ARMARIO SOLIDARIO",
    label: "ARMARIO SOLIDARIO",
    style: {
      background: DARK,
      color: "#fff",
      border: "1px solid #fff",
    },
  },
  {
    type: "ARMARIO INTELIGENTE",
    label: "ARMARIO INTELIGENTE",
    style: {
      background: DARK,
      color: GOLD,
      border: `1px solid ${GOLD}`,
    },
  },
  {
    type: "SAC MUSEUM",
    label: "SAC MUSEUM",
    style: {
      background: GOLD,
      color: "#000",
      border: "none",
      fontWeight: "bold" as const,
    },
  },
];

type Props = {
  onFilter?: (type: CollaboratorType, message: string) => void;
};

export function CollaboratorNav({ onFilter }: Props) {
  const handleClick = async (type: CollaboratorType) => {
    try {
      const r = await fetch("/api/v1/collaborators/filter", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ type }),
      });
      const data = (await r.json().catch(() => ({}))) as {
        message?: string;
      };
      const msg =
        data.message ??
        `Connexion sécurisée à ${type}. Analyse de fit en cours.`;
      onFilter?.(type, msg);
      window.alert(msg);
    } catch {
      window.alert(`Connexion sécurisée à ${type}. Analyse de fit en cours.`);
    }
  };

  return (
    <div
      style={{
        position: "fixed",
        bottom: NAV_BOTTOM_OFFSET,
        width: "100%",
        display: "flex",
        justifyContent: "center",
        gap: NAV_GAP,
        zIndex: 1003,
      }}
    >
      {BUTTONS.map((btn) => (
        <button
          key={btn.type}
          type="button"
          onClick={() => void handleClick(btn.type)}
          aria-label={`Filtrar por ${btn.label}`}
          style={{
            padding: "5px 15px",
            cursor: "pointer",
            fontSize: BTN_FONT_SIZE,
            letterSpacing: 1,
            textTransform: "uppercase",
            borderRadius: 2,
            ...btn.style,
          }}
        >
          {btn.label}
        </button>
      ))}
    </div>
  );
}
