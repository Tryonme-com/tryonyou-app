import { RefObject } from "react";
import type { Garment } from "./types";
import type { Biometrics } from "@/lib/biometrics";

interface MannequinPreviewProps {
  threeHostRef: RefObject<HTMLDivElement | null>;
  biometrics: Biometrics | null;
  activeGarment: Garment;
  setActiveGarment: (g: Garment) => void;
  garments: Garment[];
}

export function MannequinPreview({
  threeHostRef,
  biometrics,
  activeGarment,
  setActiveGarment,
  garments,
}: MannequinPreviewProps) {
  return (
    <div className="lg:col-span-5 space-y-6">
      <div className="mirror-frame aspect-square overflow-hidden bg-[var(--color-graphite)] relative">
        <div ref={threeHostRef} className="absolute inset-0" />
        <div className="absolute top-4 left-4 right-4 flex items-center justify-between text-[10px] tracking-[0.24em] uppercase text-[var(--color-or)] pointer-events-none">
          <span>P.A.U. V11</span>
          <span>Mannequin · Or</span>
        </div>
        <div className="absolute bottom-4 left-4 right-4 flex items-end justify-between text-[10px] tracking-[0.22em] uppercase text-[var(--color-fog)] pointer-events-none">
          <span>Three.js + Kalidokit</span>
          {biometrics && (
            <span className="text-[var(--color-or)]">
              Ratio S/H&nbsp;{biometrics.ratio.toFixed(2)}
            </span>
          )}
        </div>
      </div>

      <div>
        <div className="text-[10px] tracking-[0.24em] uppercase text-[var(--color-or)] mb-3">
          Sélection couture
        </div>
        <div className="grid grid-cols-1 gap-2">
          {garments.map(g => (
            <button
              key={g.id}
              onClick={() => setActiveGarment(g)}
              className={`group flex items-center justify-between gap-3 px-4 py-3 border transition-all duration-500 ${
                activeGarment.id === g.id
                  ? "border-[var(--color-or)] bg-[rgba(201,168,76,0.08)]"
                  : "border-[rgba(201,168,76,0.2)] hover:border-[rgba(201,168,76,0.5)]"
              }`}
            >
              <div className="flex items-center gap-3 text-left">
                <span
                  aria-hidden
                  className="block w-5 h-5"
                  style={{
                    background: g.color,
                    border: "1px solid rgba(201,168,76,0.4)",
                  }}
                />
                <div>
                  <div className="text-[14px] text-[var(--color-ivoire)]">
                    {g.name}
                  </div>
                  <div className="text-[10px] tracking-[0.2em] uppercase text-[var(--color-fog)]">
                    {g.category}
                  </div>
                </div>
              </div>
              <span
                className={`text-[var(--color-or)] transition-opacity ${
                  activeGarment.id === g.id
                    ? "opacity-100"
                    : "opacity-0 group-hover:opacity-60"
                }`}
              >
                ◆
              </span>
            </button>
          ))}
        </div>
      </div>

      <div className="border-t border-[rgba(201,168,76,0.25)] pt-5">
        <div className="text-[10px] tracking-[0.24em] uppercase text-[var(--color-or)] mb-2">
          Protocole
        </div>
        <p className="text-[12px] leading-[1.7] text-[var(--color-ivoire)]/70">
          Aucune image n'est envoyée à un serveur. La détection corporelle, le
          mapping squelette et le calcul d'ajustement s'exécutent intégralement
          dans votre navigateur — protocole Zéro-Profil, brevet
          PCT/EP2025/067317.
        </p>
      </div>
    </div>
  );
}
