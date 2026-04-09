import { motion } from "framer-motion";

type Props = {
  enabled: boolean;
  district: "75009" | "75004" | "";
  onSnap: () => void;
};

export function MirrorSnap({ enabled, district, onSnap }: Props) {
  const districtLabel =
    district === "75004" ? "BHV Marais 75004" : district === "75009" ? "Lafayette 75009" : "Nodo soberano";

  return (
    <motion.button
      type="button"
      className="mirror-snap-launcher"
      onClick={onSnap}
      disabled={!enabled}
      aria-label="MirrorSnap - disparo espejo digital"
      title={enabled ? `MirrorSnap activo · ${districtLabel}` : "MirrorSnap inactivo: requiere nodo autorizado"}
      whileHover={enabled ? { scale: 1.02 } : undefined}
      whileTap={enabled ? { scale: 0.98 } : undefined}
      transition={{ duration: 0.2 }}
    >
      <span className="mirror-snap-launcher__title">MirrorSnap</span>
      <span className="mirror-snap-launcher__subtitle">{enabled ? districtLabel : "Esperando autorización"}</span>
    </motion.button>
  );
}
