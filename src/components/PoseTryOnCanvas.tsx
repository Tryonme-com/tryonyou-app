/**
 * PoseTryOnCanvas — Real-time 2D garment try-on (webcam + MediaPipe Pose).
 * Patent PCT/EP2025/067317
 */
import { useEffect, useRef, useState, useCallback } from "react";
import Webcam from "react-webcam";
import {
  renderGarmentOnBody,
  smoothLandmarks,
  type PoseLandmark,
  type GarmentRenderConfig,
  type GlowOptions,
} from "../lib/renderGarmentOnBody";
import {
  computeElasticityRatio,
  fabricFitComparator,
  verdictToUiLabel,
} from "../lib/fabricFitComparator";
import { ELENA_DEMO_GARMENTS } from "../data/elenaGarments";

interface GarmentAsset {
  id: string;
  name: string;
  imagePath: string;
  config: GarmentRenderConfig;
}

interface Props {
  garments?: GarmentAsset[];
  initialIndex?: number;
  enableGlow?: boolean;
  onFitChange?: (verdict: string, label: string) => void;
}

const POSE_LANDMARKER_WASM =
  "https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision@latest/wasm";
const POSE_LANDMARKER_MODEL =
  "https://storage.googleapis.com/mediapipe-models/pose_landmarker/pose_landmarker_heavy/float16/latest/pose_landmarker_heavy.task";

const GLOW_HIGH_FIT: GlowOptions = {
  color: "#D4AF37",
  blur: 18,
  alpha: 0.35,
};

export default function PoseTryOnCanvas({
  garments = ELENA_DEMO_GARMENTS,
  initialIndex = 0,
  enableGlow = true,
  onFitChange,
}: Props) {
  const webcamRef = useRef<Webcam>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const garmentImgRef = useRef<HTMLImageElement | null>(null);
  const landmarkerRef = useRef<{ detectForVideo: (v: HTMLVideoElement, t: number) => unknown } | null>(
    null,
  );
  const rafRef = useRef<number>(0);
  const smoothedRef = useRef<PoseLandmark[] | null>(null);
  const fitFrameRef = useRef(0);
  const cameraActiveRef = useRef(false);

  const [currentIndex, setCurrentIndex] = useState(initialIndex);
  const [isLoading, setIsLoading] = useState(true);
  const [cameraActive, setCameraActive] = useState(false);
  const [fitLabel, setFitLabel] = useState("Analyse en cours…");
  const [fitScore, setFitScore] = useState(0);
  const [poseOk, setPoseOk] = useState(false);

  const currentGarment = garments[currentIndex];

  useEffect(() => {
    let cancelled = false;

    async function initPose() {
      try {
        const vision = await import("@mediapipe/tasks-vision");
        const { PoseLandmarker, FilesetResolver } = vision;

        const filesetResolver = await FilesetResolver.forVisionTasks(POSE_LANDMARKER_WASM);
        const landmarker = await PoseLandmarker.createFromOptions(filesetResolver, {
          baseOptions: {
            modelAssetPath: POSE_LANDMARKER_MODEL,
            delegate: "GPU",
          },
          runningMode: "VIDEO",
          numPoses: 1,
          minPoseDetectionConfidence: 0.65,
          minTrackingConfidence: 0.65,
        });

        if (!cancelled) {
          landmarkerRef.current = landmarker;
          setIsLoading(false);
        }
      } catch (err) {
        console.error("[PoseTryOnCanvas] PoseLandmarker init failed:", err);
        if (!cancelled) setIsLoading(false);
      }
    }

    void initPose();
    return () => {
      cancelled = true;
    };
  }, []);

  useEffect(() => {
    if (!currentGarment) return;
    smoothedRef.current = null;

    const img = new Image();
    img.crossOrigin = "anonymous";
    img.src = currentGarment.imagePath;
    img.onload = () => {
      garmentImgRef.current = img;
    };
    img.onerror = () => {
      console.warn(`[PoseTryOnCanvas] Failed to load: ${currentGarment.imagePath}`);
      garmentImgRef.current = null;
    };
  }, [currentGarment]);

  const startCamera = useCallback(async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { facingMode: "user", width: { ideal: 1280 }, height: { ideal: 720 } },
        audio: false,
      });
      const video = webcamRef.current?.video;
      if (video) {
        video.srcObject = stream;
        await video.play();
        cameraActiveRef.current = true;
        setCameraActive(true);
      }
    } catch (err) {
      console.error("[PoseTryOnCanvas] Camera denied:", err);
    }
  }, []);

  const detect = useCallback(() => {
    const video = webcamRef.current?.video;
    const canvas = canvasRef.current;
    const landmarker = landmarkerRef.current;
    const garmentImg = garmentImgRef.current;

    if (!video || !canvas || !cameraActiveRef.current || video.readyState < 2) {
      rafRef.current = requestAnimationFrame(detect);
      return;
    }

    const ctx = canvas.getContext("2d");
    if (!ctx) {
      rafRef.current = requestAnimationFrame(detect);
      return;
    }

    const vw = video.videoWidth;
    const vh = video.videoHeight;
    if (canvas.width !== vw) canvas.width = vw;
    if (canvas.height !== vh) canvas.height = vh;

    ctx.save();
    ctx.translate(vw, 0);
    ctx.scale(-1, 1);
    ctx.drawImage(video, 0, 0, vw, vh);
    ctx.restore();

    let rendered = false;

    if (landmarker && garmentImg?.complete && garmentImg.naturalWidth > 0) {
      try {
        const result = landmarker.detectForVideo(video, performance.now()) as {
          landmarks?: Array<Array<{ x: number; y: number; z?: number; visibility?: number }>>;
        };

        if (result?.landmarks?.[0]) {
          const raw: PoseLandmark[] = result.landmarks[0].map((lm) => ({
            ...lm,
            x: 1 - lm.x,
          }));
          const landmarks = smoothLandmarks(raw, smoothedRef.current);
          smoothedRef.current = landmarks;

          const elasticity = computeElasticityRatio(landmarks);
          const verdict = fabricFitComparator(elasticity);
          const label = verdictToUiLabel(verdict);

          fitFrameRef.current += 1;
          if (fitFrameRef.current % 8 === 0) {
            setFitLabel(label);
            setFitScore(Math.round(elasticity * 100));
            onFitChange?.(verdict, label);
          }

          const glow = enableGlow && verdict === "aligned" ? GLOW_HIGH_FIT : null;
          rendered = renderGarmentOnBody(
            ctx,
            garmentImg,
            landmarks,
            currentGarment.config,
            vw,
            vh,
            glow,
          );
          setPoseOk(rendered);
        } else {
          setPoseOk(false);
        }
      } catch {
        setPoseOk(false);
      }
    }

    if (!rendered) {
      setPoseOk(false);
    }

    rafRef.current = requestAnimationFrame(detect);
  }, [currentGarment, enableGlow, onFitChange]);

  useEffect(() => {
    if (!isLoading && cameraActive) {
      rafRef.current = requestAnimationFrame(detect);
    }
    return () => cancelAnimationFrame(rafRef.current);
  }, [isLoading, cameraActive, detect]);

  useEffect(() => {
    return () => {
      const video = webcamRef.current?.video;
      const stream = video?.srcObject as MediaStream | null;
      stream?.getTracks().forEach((t) => t.stop());
    };
  }, []);

  return (
    <div
      style={{
        position: "relative",
        width: "100%",
        maxWidth: 720,
        margin: "0 auto",
        borderRadius: 20,
        overflow: "hidden",
        backgroundColor: "#0B0B0D",
        border: "2px solid #C7A86A",
      }}
    >
      <Webcam
        ref={webcamRef}
        audio={false}
        mirrored={false}
        style={{ position: "absolute", opacity: 0, pointerEvents: "none", width: 1, height: 1 }}
        videoConstraints={{ facingMode: "user", width: { ideal: 1280 }, height: { ideal: 720 } }}
      />

      <canvas
        ref={canvasRef}
        style={{ width: "100%", height: "auto", display: "block", aspectRatio: "16/9" }}
      />

      {!cameraActive && (
        <div
          style={{
            position: "absolute",
            inset: 0,
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            justifyContent: "center",
            background: "rgba(11,11,13,0.92)",
            gap: 16,
          }}
        >
          <button
            type="button"
            onClick={() => void startCamera()}
            style={{
              padding: "14px 28px",
              background: "#C7A86A",
              color: "#0B0B0D",
              border: "none",
              borderRadius: 999,
              fontWeight: 700,
              letterSpacing: 2,
              fontSize: 12,
              cursor: "pointer",
            }}
          >
            ACTIVER LA CAMÉRA
          </button>
        </div>
      )}

      {isLoading && cameraActive && (
        <div
          style={{
            position: "absolute",
            inset: 0,
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            background: "rgba(11,11,13,0.7)",
            color: "#C7A86A",
            fontSize: 12,
            letterSpacing: 2,
          }}
        >
          Initializing Pose Engine…
        </div>
      )}

      {cameraActive && !isLoading && (
        <div
          style={{
            position: "absolute",
            bottom: 0,
            left: 0,
            right: 0,
            padding: "16px",
            background: "linear-gradient(transparent, rgba(11,11,13,0.95))",
            color: "#F5EFE6",
            textAlign: "center",
          }}
        >
          <p style={{ margin: "0 0 4px", color: "#C7A86A", fontWeight: 600 }}>
            {currentGarment?.name}
          </p>
          <p style={{ margin: "0 0 12px", fontSize: 12, opacity: 0.8 }}>
            {fitLabel} · {fitScore}% · {poseOk ? "Hombros OK" : "Ajusta posición"}
          </p>
          <div style={{ display: "flex", gap: 10, justifyContent: "center" }}>
            <button
              type="button"
              onClick={() => setCurrentIndex((i) => (i - 1 + garments.length) % garments.length)}
              style={btnStyle}
            >
              Previous
            </button>
            <button
              type="button"
              onClick={() => setCurrentIndex((i) => (i + 1) % garments.length)}
              style={btnStyle}
            >
              Next
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

const btnStyle: React.CSSProperties = {
  padding: "10px 22px",
  backgroundColor: "#C7A86A",
  color: "#0B0B0D",
  border: "none",
  borderRadius: 30,
  fontWeight: 700,
  cursor: "pointer",
  textTransform: "uppercase",
  letterSpacing: 1.2,
  fontSize: 11,
};
