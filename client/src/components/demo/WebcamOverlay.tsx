import { RefObject } from "react";
import type { Garment, DemoState } from "./types";

interface WebcamOverlayProps {
  videoRef: RefObject<HTMLVideoElement | null>;
  canvasRef: RefObject<HTMLCanvasElement | null>;
  state: DemoState;
  errorMsg: string;
  fitScore: number | null;
  activeGarment: Garment;
  startDemo: () => void;
  stopDemo: () => void;
}

export function WebcamOverlay({
  videoRef,
  canvasRef,
  state,
  errorMsg,
  fitScore,
  activeGarment,
  startDemo,
  stopDemo,
}: WebcamOverlayProps) {
  return (
    <div className="lg:col-span-7">
      <div className="mirror-frame aspect-[4/3] overflow-hidden bg-black relative">
        <video
          ref={videoRef}
          className="absolute inset-0 w-full h-full object-cover scale-x-[-1]"
          playsInline
          muted
        />
        <canvas
          ref={canvasRef}
          className="absolute inset-0 w-full h-full pointer-events-none"
        />

        {/* Eyebrow HUD */}
        <div className="absolute top-4 left-4 right-4 flex items-center justify-between text-[10px] tracking-[0.24em] uppercase text-[var(--color-or)] z-10">
          <span>Démo Live · MediaPipe → Kalidokit → Three.js</span>
          <span className="inline-flex items-center gap-2">
            <span
              className={`w-1.5 h-1.5 rounded-full ${
                state === "active"
                  ? "bg-[var(--color-or)] animate-pulse"
                  : "bg-[var(--color-fog)]"
              }`}
            />
            {state === "active"
              ? "En direct"
              : state === "loading"
                ? "Initialisation…"
                : state === "error"
                  ? "Erreur"
                  : "Inactif"}
          </span>
        </div>

        {/* Idle overlay */}
        {state !== "active" && (
          <div className="absolute inset-0 flex flex-col items-center justify-center bg-[rgba(10,8,7,0.78)] text-center px-8 z-20">
            <div className="roman mb-4">II</div>
            <h3 className="display-m mb-3 text-[var(--color-ivoire)]">
              Lancez votre <span className="accent-italic">essayage</span>
            </h3>
            <p className="text-[14px] leading-[1.7] text-[var(--color-ivoire)]/75 max-w-[42ch] mb-8">
              Autorisez l'accès caméra. La démo détecte 33 points clés
              MediaPipe, anime un avatar 3D Kalidokit et superpose la pièce
              choisie en temps réel. Aucune image ni mesure n'est enregistrée.
            </p>
            {state === "error" && (
              <p className="text-[12px] mb-6 text-[#E8B4B4] max-w-[42ch]">
                {errorMsg}
              </p>
            )}
            <button
              onClick={startDemo}
              disabled={state === "loading"}
              className="btn-or disabled:opacity-50 disabled:cursor-wait"
            >
              {state === "loading" ? "Initialisation…" : "Activer la caméra"}
              {state !== "loading" && <span aria-hidden>→</span>}
            </button>
            <p className="mt-6 text-[10px] tracking-[0.22em] uppercase text-[var(--color-fog)]">
              Données traitées localement · RGPD
            </p>
          </div>
        )}

        {/* Active footer — fit score */}
        {state === "active" && fitScore !== null && (
          <div className="absolute bottom-4 left-4 right-4 flex items-end justify-between gap-3 z-10">
            <div>
              <div className="text-[10px] tracking-[0.22em] uppercase text-[var(--color-fog)]">
                Pièce essayée
              </div>
              <div className="font-display italic text-[var(--color-or)] text-[20px] leading-tight">
                {activeGarment.name}
              </div>
            </div>
            <div className="text-right">
              <div className="text-[10px] tracking-[0.22em] uppercase text-[var(--color-fog)]">
                Score d'ajustement
              </div>
              <div className="font-display text-[var(--color-or)] text-[28px] leading-none">
                {fitScore}
                <span className="text-[16px]">/100</span>
              </div>
            </div>
          </div>
        )}
      </div>

      <div className="mt-4 flex items-center justify-between text-[11px] tracking-[0.2em] uppercase text-[var(--color-fog)]">
        <span>33 keypoints · 99,7 % précision</span>
        {state === "active" && (
          <button
            onClick={stopDemo}
            className="text-[var(--color-or)] hover:text-[var(--color-or-pale)] transition-colors"
          >
            Arrêter la démo →
          </button>
        )}
      </div>
    </div>
  );
}
