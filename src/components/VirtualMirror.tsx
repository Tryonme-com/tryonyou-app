import { useCallback, useEffect, useRef, useState } from "react";
import { Camera } from "@mediapipe/camera_utils";
import { drawConnectors, drawLandmarks } from "@mediapipe/drawing_utils";
import { Pose, POSE_CONNECTIONS } from "@mediapipe/pose";
import {
  computeElasticityRatio,
  fabricFitComparator,
  verdictToUiLabel,
  type NormalizedLandmark,
} from "../lib/fabricFitComparator";

const GOLD = "#C5A46D";
const WHITE = "#FFFFFF";

const EMA_ALPHA = 0.22;

type Props = {
  onStatus?: (line: string) => void;
  onElasticity?: (ema: number, verdictLabel: string) => void;
};

export function VirtualMirror({ onStatus, onElasticity }: Props) {
  const videoRef = useRef<HTMLVideoElement | null>(null);
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const emaRef = useRef(0.5);
  const startedRef = useRef(false);
  const noPoseStreakRef = useRef(0);

  const [line, setLine] = useState("Initialisation biométrique…");

  const pushStatus = useCallback(
    (s: string) => {
      setLine(s);
      onStatus?.(s);
    },
    [onStatus],
  );

  useEffect(() => {
    const videoEl = videoRef.current;
    const canvasEl = canvasRef.current;
    if (!videoEl || !canvasEl) {
      pushStatus("Interface miroir indisponible.");
      return;
    }
    const ctx = canvasEl.getContext("2d");
    if (!ctx) {
      pushStatus("Canvas indisponible.");
      return;
    }

    let pose: Pose | null = null;
    let camera: Camera | null = null;

    const fitCanvas = () => {
      const w = Math.max(1, Math.floor(window.innerWidth));
      const h = Math.max(1, Math.floor(window.innerHeight));
      canvasEl.width = w;
      canvasEl.height = h;
    };

    /* MediaPipe Results incluye GpuBuffer / ImageBitmap; drawImage acepta CanvasImageSource en runtime */
    const onResults = (results: {
      image: CanvasImageSource;
      poseLandmarks?: NormalizedLandmark[];
    }) => {
      ctx.save();
      ctx.clearRect(0, 0, canvasEl.width, canvasEl.height);
      ctx.drawImage(results.image, 0, 0, canvasEl.width, canvasEl.height);
      if (results.poseLandmarks && results.poseLandmarks.length) {
        noPoseStreakRef.current = 0;
        const ratio = computeElasticityRatio(results.poseLandmarks);
        emaRef.current = EMA_ALPHA * ratio + (1 - EMA_ALPHA) * emaRef.current;
        const verdict = fabricFitComparator(emaRef.current);
        const label = verdictToUiLabel(verdict);
        onElasticity?.(emaRef.current, label);
        pushStatus("Silhouette détectée — mode Zero-Size actif");
        drawConnectors(ctx, results.poseLandmarks, POSE_CONNECTIONS, {
          color: GOLD,
          lineWidth: 2,
        });
        drawLandmarks(ctx, results.poseLandmarks, {
          color: WHITE,
          lineWidth: 1,
          radius: 2,
        });
      } else {
        noPoseStreakRef.current += 1;
        if (noPoseStreakRef.current === 18) {
          pushStatus("Face au miroir — recherche de silhouette…");
        }
      }
      ctx.restore();
    };

    const start = async () => {
      if (startedRef.current) return;
      startedRef.current = true;
      try {
        pose = new Pose({
          locateFile: (file) =>
            `https://cdn.jsdelivr.net/npm/@mediapipe/pose/${file}`,
        });
        pose.setOptions({
          modelComplexity: 1,
          smoothLandmarks: true,
          minDetectionConfidence: 0.5,
        });
        pose.onResults(onResults as (r: object) => void);
        camera = new Camera(videoEl, {
          onFrame: async () => {
            if (pose) await pose.send({ image: videoEl });
          },
          width: 1280,
          height: 720,
        });
        await camera.start();
        pushStatus("Caméra prête — analyse en direct");
      } catch {
        pushStatus("Caméra ou MediaPipe indisponible (HTTPS requis).");
        startedRef.current = false;
      }
    };

    fitCanvas();
    void start();

    const onResize = () => fitCanvas();
    window.addEventListener("resize", onResize);

    return () => {
      window.removeEventListener("resize", onResize);
      try {
        camera?.stop();
      } catch {
        /* ignore */
      }
      try {
        pose?.close();
      } catch {
        /* ignore */
      }
      startedRef.current = false;
    };
  }, [onElasticity, pushStatus]);

  return (
    <div
      style={{
        position: "relative",
        width: "100vw",
        height: "100vh",
        background: "#000",
      }}
    >
      <div
        style={{
          position: "absolute",
          width: "100%",
          height: "2px",
          top: 0,
          zIndex: 10,
          opacity: 0.55,
          background: `linear-gradient(90deg, transparent, ${GOLD}, transparent)`,
          animation: "ty-scan 3s infinite ease-in-out",
        }}
      />
      <style>{`
        @keyframes ty-scan {
          0% { top: 0%; }
          50% { top: 100%; }
          100% { top: 0%; }
        }
      `}</style>
      <video
        ref={videoRef}
        style={{ display: "none" }}
        playsInline
        muted
      />
      <canvas
        ref={canvasRef}
        style={{
          position: "absolute",
          inset: 0,
          width: "100%",
          height: "100%",
          objectFit: "cover",
          transform: "scaleX(-1)",
        }}
      />
      <div
        style={{
          position: "absolute",
          top: 24,
          left: "50%",
          transform: "translateX(-50%)",
          zIndex: 20,
          fontSize: 11,
          letterSpacing: 2,
          padding: "8px 14px",
          borderRadius: 999,
          border: `1px solid ${GOLD}`,
          background: "rgba(0,0,0,0.45)",
          color: "var(--bone)",
          pointerEvents: "none",
        }}
      >
        {line}
      </div>
    </div>
  );
}
