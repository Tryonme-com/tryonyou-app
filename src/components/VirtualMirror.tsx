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

const EMA_ALPHA = 0.22;

function drawBalmainWhiteTorso(
  ctx: CanvasRenderingContext2D,
  lm: NormalizedLandmark[],
  w: number,
  h: number,
) {
  if (!lm || lm.length < 25) return;
  const xy = (i: number) => ({ x: lm[i].x * w, y: lm[i].y * h });
  const ls = xy(11),
    rs = xy(12),
    lh = xy(23),
    rh = xy(24);
  ctx.save();
  ctx.fillStyle = "rgba(255,255,255,0.36)";
  ctx.strokeStyle = "rgba(197, 164, 109, 0.5)";
  ctx.lineWidth = 2;
  ctx.beginPath();
  ctx.moveTo(ls.x, ls.y);
  ctx.lineTo(rs.x, rs.y);
  ctx.lineTo(rh.x, rh.y + h * 0.022);
  ctx.lineTo(lh.x, lh.y + h * 0.022);
  ctx.closePath();
  ctx.fill();
  ctx.stroke();
  ctx.restore();
}

type Props = {
  revealBalmainSuit?: boolean;
  onStatus?: (line: string) => void;
  /** Zero-Size: solo veredicto emocional en UI, sin EMA ni números. */
  onFitVerdict?: (verdictLabel: string) => void;
};

export function VirtualMirror({
  revealBalmainSuit = false,
  onStatus,
  onFitVerdict,
}: Props) {
  const videoRef = useRef<HTMLVideoElement | null>(null);
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const emaRef = useRef(0.5);
  const startedRef = useRef(false);
  const noPoseStreakRef = useRef(0);
  const revealRef = useRef(revealBalmainSuit);

  const [line, setLine] = useState("Initialisation biométrique…");

  useEffect(() => {
    revealRef.current = revealBalmainSuit;
  }, [revealBalmainSuit]);

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

    const onResults = (results: {
      image: CanvasImageSource;
      poseLandmarks?: NormalizedLandmark[];
    }) => {
      ctx.save();
      ctx.clearRect(0, 0, canvasEl.width, canvasEl.height);
      ctx.drawImage(results.image, 0, 0, canvasEl.width, canvasEl.height);
      if (results.poseLandmarks && results.poseLandmarks.length >= 33) {
        noPoseStreakRef.current = 0;
        const ratio = computeElasticityRatio(results.poseLandmarks);
        emaRef.current = EMA_ALPHA * ratio + (1 - EMA_ALPHA) * emaRef.current;
        const verdict = fabricFitComparator(emaRef.current);
        const label = verdictToUiLabel(verdict);
        onFitVerdict?.(label);
        pushStatus("Silhouette détectée — mode Zero-Size actif");
        drawConnectors(ctx, results.poseLandmarks, POSE_CONNECTIONS, {
          color: GOLD,
          lineWidth: 2,
        });
        drawLandmarks(ctx, results.poseLandmarks, {
          color: GOLD,
          lineWidth: 1,
          radius: 2,
        });
        if (revealRef.current) {
          drawBalmainWhiteTorso(
            ctx,
            results.poseLandmarks,
            canvasEl.width,
            canvasEl.height,
          );
        }
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
  }, [onFitVerdict, pushStatus]);

  return (
    <div
      style={{
        position: "relative",
        width: "100%",
        height: "100%",
        minHeight: "100%",
        background: "#000",
      }}
    >
      <div className="mirror-scan" aria-hidden />
      <video ref={videoRef} className="mirror-video-hidden" playsInline muted />
      <canvas ref={canvasRef} className="mirror-canvas" />
      <div className="mirror-status">{line}</div>
    </div>
  );
}
