/**
 * PoseTryOnCanvas — Real-time 2D garment try-on using webcam + MediaPipe Pose.
 *
 * This component replaces the static overlay approach in VirtualMirror.jsx
 * with a landmark-anchored Canvas renderer that tracks the user's body
 * in real time and overlays garment PNGs with fabric-realistic compositing.
 *
 * Dependencies:
 *   - @mediapipe/tasks-vision (PoseLandmarker)
 *   - react-webcam
 *
 * Patent PCT/EP2025/067317 — TRYONYOU–ABVETOS–ULTRA–PLUS–ULTIMATUM
 * Protocol: Divineo V11 — Zero-Size Sovereign Fit
 */
import { useEffect, useRef, useState, useCallback } from "react";
import Webcam from "react-webcam";
import {
  renderGarmentOnBody,
  adaptLegacyOverlay,
  type PoseLandmark,
  type GarmentRenderConfig,
  type GlowOptions,
} from "../lib/renderGarmentOnBody";
import {
  computeElasticityRatio,
  fabricFitComparator,
  verdictToUiLabel,
} from "../lib/fabricFitComparator";

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

interface GarmentAsset {
  id: string;
  name: string;
  imagePath: string;
  config: GarmentRenderConfig;
}

interface Props {
  /** Array of garments available for try-on. */
  garments: GarmentAsset[];
  /** Initial garment index. */
  initialIndex?: number;
  /** Enable/disable the golden glow on high fit-score. */
  enableGlow?: boolean;
  /** Callback when fit verdict changes. */
  onFitChange?: (verdict: string, label: string) => void;
}

// ---------------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------------

const POSE_LANDMARKER_WASM =
  "https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision@latest/wasm";
const POSE_LANDMARKER_MODEL =
  "https://storage.googleapis.com/mediapipe-models/pose_landmarker/pose_landmarker_heavy/float16/latest/pose_landmarker_heavy.task";

const GLOW_HIGH_FIT: GlowOptions = {
  color: "#D4AF37",
  blur: 18,
  alpha: 0.35,
};

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

export default function PoseTryOnCanvas({
  garments,
  initialIndex = 0,
  enableGlow = true,
  onFitChange,
}: Props) {
  const webcamRef = useRef<Webcam>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const garmentImgRef = useRef<HTMLImageElement | null>(null);
  const landmarkerRef = useRef<any>(null);
  const rafRef = useRef<number>(0);

  const [currentIndex, setCurrentIndex] = useState(initialIndex);
  const [isLoading, setIsLoading] = useState(true);
  const [fitLabel, setFitLabel] = useState("Analyzing...");
  const [fitScore, setFitScore] = useState(0);

  const currentGarment = garments[currentIndex];

  // -------------------------------------------------------------------------
  // Load MediaPipe Pose Landmarker
  // -------------------------------------------------------------------------
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
          minPoseDetectionConfidence: 0.5,
          minTrackingConfidence: 0.5,
        });

        if (!cancelled) {
          landmarkerRef.current = landmarker;
          setIsLoading(false);
        }
      } catch (err) {
        console.error("[PoseTryOnCanvas] Failed to init PoseLandmarker:", err);
        if (!cancelled) setIsLoading(false);
      }
    }

    initPose();
    return () => {
      cancelled = true;
    };
  }, []);

  // -------------------------------------------------------------------------
  // Load garment image
  // -------------------------------------------------------------------------
  useEffect(() => {
    if (!currentGarment) return;

    const img = new Image();
    img.crossOrigin = "anonymous";
    img.src = currentGarment.imagePath;
    img.onload = () => {
      garmentImgRef.current = img;
    };
    img.onerror = () => {
      console.warn(`[PoseTryOnCanvas] Failed to load garment: ${currentGarment.imagePath}`);
      garmentImgRef.current = null;
    };
  }, [currentGarment]);

  // -------------------------------------------------------------------------
  // Animation loop
  // -------------------------------------------------------------------------
  const detect = useCallback(() => {
    const video = webcamRef.current?.video;
    const canvas = canvasRef.current;
    const landmarker = landmarkerRef.current;
    const garmentImg = garmentImgRef.current;

    if (!video || !canvas || !landmarker || video.readyState < 2) {
      rafRef.current = requestAnimationFrame(detect);
      return;
    }

    const ctx = canvas.getContext("2d");
    if (!ctx) {
      rafRef.current = requestAnimationFrame(detect);
      return;
    }

    // Match canvas to video dimensions
    const vw = video.videoWidth;
    const vh = video.videoHeight;
    if (canvas.width !== vw) canvas.width = vw;
    if (canvas.height !== vh) canvas.height = vh;

    // Run pose detection
    const now = performance.now();
    const result = landmarker.detectForVideo(video, now);

    // Clear and draw mirrored video frame
    ctx.save();
    ctx.translate(vw, 0);
    ctx.scale(-1, 1);
    ctx.drawImage(video, 0, 0, vw, vh);
    ctx.restore();

    // Overlay garment if landmarks available
    if (result?.landmarks?.[0] && garmentImg && currentGarment) {
      const landmarks: PoseLandmark[] = result.landmarks[0].map((lm: any) => ({
        ...lm,
        x: 1 - lm.x // Inversión de espejo horizontal para sincronizar con ctx.scale
      }));

      // Compute fit verdict
      const elasticity = computeElasticityRatio(landmarks);
      const verdict = fabricFitComparator(elasticity);
      const label = verdictToUiLabel(verdict);
      setFitLabel(label);
      setFitScore(Math.round(elasticity * 100));
      onFitChange?.(verdict, label);

      // Determine glow based on fit
      const glow =
        enableGlow && verdict === "aligned" ? GLOW_HIGH_FIT : null;

      renderGarmentOnBody(
        ctx,
        garmentImg,
        landmarks,
        currentGarment.config,
        vw,
        vh,
        glow,
      );
    }

    rafRef.current = requestAnimationFrame(detect);
  }, [currentGarment, enableGlow, onFitChange]);

  useEffect(() => {
    if (!isLoading) {
      rafRef.current = requestAnimationFrame(detect);
    }
    return () => {
      cancelAnimationFrame(rafRef.current);
    };
  }, [isLoading, detect]);

  // -------------------------------------------------------------------------
  // Garment cycling
  // -------------------------------------------------------------------------
  const cycleNext = () => {
    setCurrentIndex((prev) => (prev + 1) % garments.length);
  };

  const cyclePrev = () => {
    setCurrentIndex((prev) => (prev - 1 + garments.length) % garments.length);
  };

  // -------------------------------------------------------------------------
  // Render
  // -------------------------------------------------------------------------
  return (
    <div
      style={{
        position: "relative",
        width: "100%",
        maxWidth: 640,
        margin: "0 auto",
        borderRadius: 20,
        overflow: "hidden",
        backgroundColor: "#0E0A08",
        border: "2px solid #C5A46D",
      }}
    >
      {/* Hidden webcam (video source only) */}
      <Webcam
        ref={webcamRef}
        audio={false}
        mirrored={false}
        style={{ position: "absolute", opacity: 0, pointerEvents: "none" }}
        videoConstraints={{
          facingMode: "user",
          width: { ideal: 1280 },
          height: { ideal: 720 },
        }}
      />

      {/* Main canvas — video + garment overlay */}
      <canvas
        ref={canvasRef}
        style={{
          width: "100%",
          height: "auto",
          display: "block",
          aspectRatio: "16/9",
        }}
      />

      {/* Loading state */}
      {isLoading && (
        <div
          style={{
            position: "absolute",
            inset: 0,
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            justifyContent: "center",
            backgroundColor: "rgba(14, 10, 8, 0.85)",
            backdropFilter: "blur(8px)",
          }}
        >
          <div
            style={{
              width: "60%",
              height: 2,
              backgroundColor: "#C5A46D",
              boxShadow: "0 0 15px #C5A46D",
              animation: "scan 2s infinite",
            }}
          />
          <p
            style={{
              color: "#C5A46D",
              marginTop: 20,
              fontFamily: "monospace",
              letterSpacing: 2,
              textTransform: "uppercase",
              fontSize: 12,
            }}
          >
            Initializing Pose Engine...
          </p>
        </div>
      )}

      {/* Bottom panel — garment info + controls */}
      {!isLoading && (
        <div
          style={{
            position: "absolute",
            bottom: 0,
            left: 0,
            right: 0,
            padding: "20px 16px",
            background: "linear-gradient(transparent, rgba(14, 10, 8, 0.92))",
            color: "#F5EFE6",
            textAlign: "center",
          }}
        >
          <h3
            style={{
              margin: "0 0 4px",
              color: "#C5A46D",
              fontSize: 16,
              fontWeight: 600,
            }}
          >
            {currentGarment?.name ?? "—"}
          </h3>
          <p
            style={{
              margin: "0 0 14px",
              fontSize: 12,
              opacity: 0.75,
              letterSpacing: 0.8,
            }}
          >
            {fitLabel} | Elasticity: {fitScore}%
          </p>

          <div style={{ display: "flex", gap: 12, justifyContent: "center" }}>
            <button
              onClick={cyclePrev}
              style={btnStyle}
              aria-label="Previous garment"
            >
              Previous
            </button>
            <button
              onClick={cycleNext}
              style={btnStyle}
              aria-label="Next garment"
            >
              Next
            </button>
          </div>
        </div>
      )}

      <style>{`
        @keyframes scan {
          0% { transform: translateY(-60px); opacity: 0.6; }
          50% { transform: translateY(60px); opacity: 1; }
          100% { transform: translateY(-60px); opacity: 0.6; }
        }
      `}</style>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Styles
// ---------------------------------------------------------------------------

const btnStyle: React.CSSProperties = {
  padding: "10px 22px",
  backgroundColor: "#C5A46D",
  color: "#0E0A08",
  border: "none",
  borderRadius: 30,
  fontWeight: 700,
  cursor: "pointer",
  textTransform: "uppercase",
  letterSpacing: 1.2,
  fontSize: 11,
};
