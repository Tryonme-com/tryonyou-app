/**
 * Maison Couture Nocturne — DigitalMirrorPanel
 *
 * Adapted from `Tryonme-com/tryonyou-app/src/components/DigitalMirrorPanel.tsx`.
 * In-browser simulation of the boutique mirror: scan animation, 5 personalized
 * suggestions, "perfect selection / fitting room / save silhouette" actions.
 *
 * No backend dependency — pure UX demo for executives.
 */
import { useCallback, useState } from "react";
import { toast } from "sonner";

type Suggestion = {
  id: string;
  name: string;
  price: number;
  fit: string;
};

const SUGGESTIONS: Suggestion[] = [
  { id: "L1", name: "Robe Soirée Couture · Or", price: 1490, fit: "Sovereign Fit" },
  { id: "L2", name: "Tailleur Smoking · Noir", price: 2280, fit: "Sovereign Fit" },
  { id: "L3", name: "Trench Long · Camel", price: 1180, fit: "Editorial Fit" },
  { id: "L4", name: "Chemise Soie · Ivoire", price: 480, fit: "Editorial Fit" },
  { id: "L5", name: "Pantalon Cigarette · Graphite", price: 590, fit: "Sovereign Fit" },
];

type Phase = "idle" | "scanning" | "ready";

export default function DigitalMirrorPanel() {
  const [phase, setPhase] = useState<Phase>("idle");
  const [active, setActive] = useState<Suggestion | null>(null);
  const [viewingAll, setViewingAll] = useState(false);

  const handleScan = useCallback(() => {
    setPhase("scanning");
    setActive(null);
    setViewingAll(false);
    window.setTimeout(() => {
      setPhase("ready");
      setActive(SUGGESTIONS[0]);
    }, 2200);
  }, []);

  const reset = useCallback(() => {
    setPhase("idle");
    setActive(null);
    setViewingAll(false);
  }, []);

  return (
    <div className="border border-[rgba(201,168,76,0.3)] bg-[rgba(10,8,7,0.6)] backdrop-blur-sm">
      <div className="flex items-center justify-between px-6 py-4 border-b border-[rgba(201,168,76,0.2)]">
        <div className="flex items-center gap-3">
          <span className="text-[var(--color-or)] font-display italic text-[20px]">
            Miroir Digital
          </span>
          <span className="text-[10px] tracking-[0.24em] uppercase text-[var(--color-fog)]">
            V11 · Boutique
          </span>
        </div>
        <span className="inline-flex items-center gap-2 text-[10px] tracking-[0.22em] uppercase text-[var(--color-or)]">
          <span
            className={`w-1.5 h-1.5 rounded-full ${
              phase === "scanning"
                ? "bg-[var(--color-or)] animate-pulse"
                : phase === "ready"
                ? "bg-[var(--color-or)]"
                : "bg-[var(--color-fog)]"
            }`}
          />
          {phase === "scanning" ? "Analyse en cours" : phase === "ready" ? "Prêt" : "En veille"}
        </span>
      </div>

      <div className="p-6 md:p-8">
        {phase === "idle" && (
          <div className="flex flex-col items-center justify-center text-center py-12">
            <div className="roman mb-4">III</div>
            <p className="text-[14px] leading-[1.7] text-[var(--color-ivoire)]/80 max-w-[44ch] mb-8">
              Lancez le scan pour découvrir vos cinq suggestions couture, calculées
              sur votre silhouette et adaptées à l'occasion sélectionnée.
            </p>
            <button onClick={handleScan} className="btn-or">
              Lancer le scan biométrique
              <span aria-hidden>→</span>
            </button>
          </div>
        )}

        {phase === "scanning" && (
          <div className="flex flex-col items-center justify-center py-16">
            <div className="relative w-32 h-32 mb-8">
              <span className="absolute inset-0 rounded-full border border-[var(--color-or)] animate-ping opacity-50" />
              <span className="absolute inset-2 rounded-full border border-[var(--color-or)] animate-pulse" />
              <span className="absolute inset-6 rounded-full bg-[var(--color-or)] opacity-30" />
              <span className="absolute inset-0 flex items-center justify-center font-display italic text-[var(--color-or)] text-[28px]">
                P
              </span>
            </div>
            <p className="text-[12px] tracking-[0.24em] uppercase text-[var(--color-or)] mb-2">
              Analyse biométrique en cours
            </p>
            <p className="text-[12px] text-[var(--color-fog)]">Protocole chiffré · Données locales</p>
          </div>
        )}

        {phase === "ready" && (
          <>
            <div className="flex items-center justify-between mb-5">
              <span className="text-[10px] tracking-[0.24em] uppercase text-[var(--color-or)]">
                Vos suggestions · 5
              </span>
              <button
                onClick={() => setViewingAll((s) => !s)}
                className="text-[11px] tracking-[0.2em] uppercase text-[var(--color-fog)] hover:text-[var(--color-or)] transition-colors"
              >
                {viewingAll ? "Réduire" : "Tout voir"}
              </button>
            </div>

            <div className="space-y-2 mb-6">
              {(viewingAll ? SUGGESTIONS : SUGGESTIONS.slice(0, 3)).map((s) => (
                <button
                  key={s.id}
                  onClick={() => setActive(s)}
                  className={`w-full flex items-center justify-between gap-3 px-4 py-3 border transition-all duration-500 ${
                    active?.id === s.id
                      ? "border-[var(--color-or)] bg-[rgba(201,168,76,0.08)]"
                      : "border-[rgba(201,168,76,0.2)] hover:border-[rgba(201,168,76,0.5)]"
                  }`}
                >
                  <div className="text-left">
                    <div className="text-[14px] text-[var(--color-ivoire)]">{s.name}</div>
                    <div className="text-[10px] tracking-[0.22em] uppercase text-[var(--color-fog)]">
                      {s.fit}
                    </div>
                  </div>
                  <span className="font-display text-[var(--color-or)] text-[18px]">
                    {new Intl.NumberFormat("fr-FR", { style: "currency", currency: "EUR", maximumFractionDigits: 0 }).format(s.price)}
                  </span>
                </button>
              ))}
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-3 mb-6">
              <button
                className="btn-or w-full justify-center text-[11px]"
                disabled={!active}
                onClick={() => toast.success("Look ajouté à votre sélection avec l'ajustement calculé.")}
              >
                Ma sélection parfaite
              </button>
              <button
                className="btn-ghost w-full justify-center text-[11px]"
                disabled={!active}
                onClick={() => toast.success("QR cabine généré — réservation confirmée.")}
              >
                <span>Réserver en cabine</span>
              </button>
              <button
                className="btn-ghost w-full justify-center text-[11px]"
                onClick={() => toast.success("Silhouette enregistrée sous protocole chiffré.")}
              >
                <span>Enregistrer ma silhouette</span>
              </button>
              <button
                className="btn-ghost w-full justify-center text-[11px]"
                disabled={!active}
                onClick={() => toast.success("Image de partage générée — données biométriques retirées.")}
              >
                <span>Partager le look</span>
              </button>
            </div>

            <div className="flex items-center justify-between pt-5 border-t border-[rgba(201,168,76,0.18)]">
              <button
                onClick={reset}
                className="text-[11px] tracking-[0.2em] uppercase text-[var(--color-fog)] hover:text-[var(--color-or)] transition-colors"
              >
                ← Recommencer
              </button>
              <span className="text-[10px] tracking-[0.22em] uppercase text-[var(--color-fog)]">
                Brevet PCT/EP2025/067317
              </span>
            </div>
          </>
        )}
      </div>
    </div>
  );
}
