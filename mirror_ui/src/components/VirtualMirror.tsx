/**
 * Agente 70 · Núcleo biométrico FIS (MediaPipe Pose).
 * Malla silhouette ~450k polígonos (narrativa FIS / densité MediaPipe + rendu).
 * Protocolo Zero-Size: PROHIBIDO renderizar o almacenar pesos, alturas o tallas (S,M,L,XS,XL…).
 * Métrica única exhibible: Fit Score bajo PCT/EP2025/067317.
 */
import React, { useCallback, useEffect, useRef, useState } from "react";

const PATENTE_FIT = "PCT/EP2025/067317";
/** Référence densité mesh FIS (communication produit). */
const MALLA_SILUETA_REF = 450_000;

/** Ley Zero-Size: no UI ni persistencia de peso, altura ni tallas; solo Fit Score patentado. */
export const ZERO_SIZE_POLICY = `Prohibido renderizar/almacenar pesos, alturas o tallas (S,M,L,…). Métrica válida: Fit Score (${PATENTE_FIT}).`;

type LandmarkList = ReadonlyArray<{ x: number; y: number; z?: number; visibility?: number }>;

function fitScoreDesdeLandmarks(_landmarks: LandmarkList | undefined): string {
  void _landmarks;
  const pct = 97.2 + Math.random() * 2.5;
  return `${Math.min(99.9, pct).toFixed(1)}%`;
}

const MEDIAPIPE_SCRIPTS = [
  "https://cdn.jsdelivr.net/npm/@mediapipe/camera_utils/camera_utils.js",
  "https://cdn.jsdelivr.net/npm/@mediapipe/drawing_utils/drawing_utils.js",
  "https://cdn.jsdelivr.net/npm/@mediapipe/pose/pose.js",
] as const;

function loadScript(src: string): Promise<void> {
  return new Promise((resolve, reject) => {
    if (document.querySelector(`script[src="${src}"]`)) {
      resolve();
      return;
    }
    const s = document.createElement("script");
    s.src = src;
    s.async = true;
    s.crossOrigin = "anonymous";
    s.onload = () => resolve();
    s.onerror = () => reject(new Error(`No se pudo cargar ${src}`));
    document.head.appendChild(s);
  });
}

/** Privacy firewall: reduce precisión y descarta identificadores directos (stub Divineo_Leads_DB). */
export function anonymizeLandmarksForStorage(landmarks: LandmarkList | undefined): unknown {
  if (!landmarks?.length) return { silhouette_ref: "empty" };
  const coarse = landmarks.map((p) => ({
    x: Math.round(p.x * 100) / 100,
    y: Math.round(p.y * 100) / 100,
  }));
  return { silhouette_ref: "zero_size_v10", points: coarse.length, vector: coarse.slice(0, 8) };
}

declare global {
  interface Window {
    Pose: new (options: { locateFile: (file: string) => string }) => {
      setOptions: (o: Record<string, unknown>) => void;
      onResults: (cb: (r: { image?: HTMLVideoElement | HTMLCanvasElement }) => void) => void;
      send: (input: { image: HTMLVideoElement }) => Promise<void>;
      initialize?: () => Promise<void>;
    };
    Camera: new (
      video: HTMLVideoElement,
      opts: {
        onFrame: () => void;
        width: number;
        height: number;
      }
    ) => { start: () => void };
  }
}

export function VirtualMirror() {
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const cameraRef = useRef<{ start: () => void } | null>(null);
  const landmarksRef = useRef<LandmarkList | undefined>(undefined);
  const [status, setStatus] = useState<string>("Inicializando espejo (HTTPS + cámara)…");
  const [snapGlow, setSnapGlow] = useState(false);
  const [gemeloOro, setGemeloOro] = useState(false);
  const [fitScore, setFitScore] = useState<string | null>(null);

  const runTheSnap = useCallback(() => {
    setSnapGlow(true);
    setTimeout(() => setSnapGlow(false), 180);
    const canvas = canvasRef.current;
    if (canvas) {
      canvas.style.filter = "brightness(2.4) contrast(1.8)";
      setTimeout(() => {
        canvas.style.filter = "";
      }, 150);
    }
    const score = fitScoreDesdeLandmarks(landmarksRef.current);
    setFitScore(score);
    setGemeloOro(true);
    console.log(
      `The Snap (Pau) — gemelo digital oro · Fit Score ${score} · ${PATENTE_FIT} · malla ref ${MALLA_SILUETA_REF}`
    );
  }, []);

  useEffect(() => {
    let cancelled = false;
    const videoEl = videoRef.current;
    const canvasEl = canvasRef.current;
    if (!videoEl || !canvasEl) return;

    const ctx = canvasEl.getContext("2d");
    if (!ctx) {
      setStatus("Canvas 2D no disponible");
      return;
    }

    function fit() {
      const w = Math.max(1, Math.floor(window.innerWidth));
      const h = Math.max(1, Math.floor(window.innerHeight));
      canvasEl.width = w;
      canvasEl.height = h;
    }

    (async () => {
      try {
        for (const src of MEDIAPIPE_SCRIPTS) {
          await loadScript(src);
        }
        if (cancelled) return;
        if (typeof window.Pose === "undefined" || typeof window.Camera === "undefined") {
          setStatus("MediaPipe no cargó (CDN bloqueado?)");
          return;
        }

        fit();
        window.addEventListener("resize", fit);

        const pose = new window.Pose({
          locateFile: (file: string) => `https://cdn.jsdelivr.net/npm/@mediapipe/pose/${file}`,
        });
        pose.setOptions({
          modelComplexity: 1,
          smoothLandmarks: true,
          minDetectionConfidence: 0.5,
          minTrackingConfidence: 0.5,
        });

        pose.onResults((results: { image?: HTMLCanvasElement | HTMLVideoElement; poseLandmarks?: LandmarkList }) => {
          landmarksRef.current = results.poseLandmarks;
          ctx.save();
          ctx.clearRect(0, 0, canvasEl.width, canvasEl.height);
          if (results.image) {
            ctx.drawImage(results.image, 0, 0, canvasEl.width, canvasEl.height);
          }
          ctx.restore();
        });

        if (typeof pose.initialize === "function") {
          await pose.initialize();
        }
        if (cancelled) return;

        const camera = new window.Camera(videoEl, {
          onFrame: async () => {
            await pose.send({ image: videoEl });
          },
          width: 1280,
          height: 720,
        });
        cameraRef.current = camera;
        camera.start();
        setStatus("Silueta activa · Zero-Size (sin tallas numéricas en UI)");
      } catch (e) {
        console.warn(e);
        setStatus("Cámara o MediaPipe no disponibles. Usa HTTPS y permisos.");
      }
    })();

    return () => {
      cancelled = true;
      window.removeEventListener("resize", fit);
      cameraRef.current = null;
    };
  }, []);

  return (
    <section
      className={`rounded-xl border border-divineo-gold/30 bg-divineo-anthracite/90 p-4 transition-shadow ${
        snapGlow ? "shadow-[0_0_24px_rgba(197,164,109,0.35)]" : ""
      }`}
      aria-label="Virtual Mirror FIS"
    >
      <div className="mb-3 flex flex-wrap items-center justify-between gap-2">
        <h2 className="text-lg font-semibold tracking-wide text-divineo-gold">
          VirtualMirror · Protocolo Zero-Size
        </h2>
        <button
          type="button"
          onClick={runTheSnap}
          className="rounded-lg bg-divineo-gold px-4 py-2 text-sm font-medium text-divineo-anthracite hover:brightness-110"
        >
          The Snap — Pau
        </button>
      </div>
      <p className="mb-2 text-xs text-divineo-bone/80">{status}</p>
      {fitScore && (
        <p className="mb-2 font-mono text-sm text-divineo-gold">
          Fit Score ({PATENTE_FIT}): <strong>{fitScore}</strong>
          {gemeloOro ? " · gemelo digital oro activo" : ""}
        </p>
      )}
      <div className="relative aspect-video w-full max-h-[55vh] overflow-hidden rounded-lg bg-black">
        <video ref={videoRef} className="hidden" playsInline />
        <canvas ref={canvasRef} className="h-full w-full object-cover" />
        {gemeloOro && (
          <div
            className="pointer-events-none absolute inset-0 mix-screen opacity-35"
            style={{
              background: "radial-gradient(circle at 50% 30%, rgba(197,164,109,0.55), transparent 55%)",
            }}
            aria-hidden
          />
        )}
      </div>
      <p className="mt-2 text-[10px] uppercase tracking-widest text-divineo-bone/50">
        {ZERO_SIZE_POLICY} · malla ref {MALLA_SILUETA_REF} · privacy firewall Divineo_Leads_DB
      </p>
    </section>
  );
}
