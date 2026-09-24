/**
 * Dress Me in Balmain — Immersive Virtual Try-On Module.
 *
 * Physics-driven fabric simulation using Verlet cloth dynamics,
 * anchored to MediaPipe Pose landmarks for real-time body tracking.
 *
 * Features:
 * - Real-time pose detection (MediaPipe PoseLandmarker GPU)
 * - Cloth physics simulation (Verlet integration + body collision)
 * - Material-specific drape behavior (neoprene, tweed, silk, leather)
 * - Divineo Glow on high fit-score (>95%)
 * - Elegant transitions with blur masking (Magic Mirror UX)
 * - Curated Selection terminology
 *
 * Patent PCT/EP2025/067317 — TRYONYOU–ABVETOS–ULTRA–PLUS–ULTIMATUM
 * Module: Balmain Sovereign Fit — Physics-Driven Couture Intelligence
 *
 * IMPORTANT: This module uses Balmain garment imagery under a pending
 * licensing agreement. See /docs/balmain-license-request.md for status.
 */
import { useEffect, useRef, useState, useCallback, useMemo } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  PhysicsGarmentEngine,
  FABRIC_MATERIALS,
  type FabricMaterial,
} from "../lib/clothPhysicsEngine";
import {
  renderGarmentOnBody,
  type PoseLandmark,
  type GlowOptions,
} from "../lib/renderGarmentOnBody";
import {
  computeElasticityRatio,
  fabricFitComparator,
  verdictToUiLabel,
} from "../lib/fabricFitComparator";
import { mirrorDigitalMiddleware } from "../lib/mirrorDigitalMiddleware";

// ---------------------------------------------------------------------------
// Balmain Catalog — Curated Selection
// ---------------------------------------------------------------------------

export interface BalmainGarment {
  id: string;
  name: string;
  collection: string;
  imagePath: string;
  material: FabricMaterial;
  /** Shoulder-to-image-width ratio for fallback renderer. */
  shoulderWidthRatio: number;
  /** Neck anchor Y ratio for fallback renderer. */
  neckY: number;
  /** Price in EUR (display only). */
  priceEur: number;
  /** Fabric science description. */
  fabricScience: string;
}

/**
 * Balmain Curated Collection — Physics-Mapped Garments.
 * Each garment is mapped to a specific FabricMaterial for accurate drape simulation.
 */
export const BALMAIN_COLLECTION: BalmainGarment[] = [
  {
    id: "blm_blazer_pierre",
    name: "Blazer Croisé Structuré Pierre",
    collection: "Automne-Hiver 2025",
    imagePath: "/assets/balmain_blazer.png",
    material: FABRIC_MATERIALS.neoprene,
    shoulderWidthRatio: 0.42,
    neckY: 0.15,
    priceEur: 3290,
    fabricScience:
      "Neoprene satin composite (82% polyester, 18% elastane). Stiffness coefficient: 0.97. " +
      "Minimal drape — structured silhouette maintained by internal boning and heat-bonded seams. " +
      "Physics model: high shear resistance, low gravitational deformation.",
  },
  {
    id: "blm_dress_monogram",
    name: "Robe Tricot Monogramme Géométrique",
    collection: "Croisière 2025",
    imagePath: "/assets/balmain_dress.png",
    material: FABRIC_MATERIALS.cotton,
    shoulderWidthRatio: 0.40,
    neckY: 0.12,
    priceEur: 2150,
    fabricScience:
      "Jacquard knit (95% viscose, 5% elastane). Elasticity ratio: 1.15. " +
      "Medium drape with body-conforming stretch. Physics model: moderate structural stiffness " +
      "with high shear flexibility allowing diagonal deformation along body contours.",
  },
  {
    id: "blm_tweed_vintage",
    name: "Veste Tweed Boutons Or Vintage",
    collection: "Haute Couture SS25",
    imagePath: "/assets/balmain_tweed.png",
    material: FABRIC_MATERIALS.tweed,
    shoulderWidthRatio: 0.44,
    neckY: 0.14,
    priceEur: 4890,
    fabricScience:
      "Bouclé tweed (65% wool, 25% cotton, 10% silk). Bend stiffness: 0.70. " +
      "Structured drape with textural surface irregularity. Physics model: high bend resistance " +
      "creates box-like silhouette; shear constraints prevent diagonal collapse.",
  },
  {
    id: "blm_corset_neoprene",
    name: "Top Corset Néoprène Satiné",
    collection: "Automne-Hiver 2025",
    imagePath: "/assets/balmain_corset.png",
    material: FABRIC_MATERIALS.neoprene,
    shoulderWidthRatio: 0.38,
    neckY: 0.08,
    priceEur: 1890,
    fabricScience:
      "Double-face neoprene (100% chloroprene rubber, satin laminate). Stiffness: 0.97. " +
      "Zero drape — garment maintains form independent of body movement. " +
      "Physics model: near-rigid body with minimal particle displacement under gravity.",
  },
  {
    id: "blm_coat_masculine",
    name: "Manteau Long Masculin Laine Noire",
    collection: "Automne-Hiver 2025",
    imagePath: "/assets/balmain_coat.png",
    material: FABRIC_MATERIALS.wool,
    shoulderWidthRatio: 0.46,
    neckY: 0.10,
    priceEur: 5490,
    fabricScience:
      "Virgin wool gabardine (100% wool, 320g/m²). Gravity scale: 0.9. " +
      "Heavy structured drape with pendular swing on movement. Physics model: high mass " +
      "creates momentum-driven fabric motion; bend stiffness maintains lapel structure.",
  },
  {
    id: "blm_organza_evening",
    name: "Robe du Soir Organza Plissé",
    collection: "Haute Couture SS25",
    imagePath: "/assets/balmain_evening.png",
    material: FABRIC_MATERIALS.organza,
    shoulderWidthRatio: 0.39,
    neckY: 0.11,
    priceEur: 12800,
    fabricScience:
      "Silk organza (100% mulberry silk, 6 momme). Bend stiffness: 0.05. " +
      "Maximum drape with ethereal floating behavior. Physics model: ultra-low mass " +
      "with high gravity sensitivity creates cascading wave patterns; wind response amplified.",
  },
];

// ---------------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------------

const GLOW_BALMAIN: GlowOptions = {
  color: "#D4AF37",
  blur: 22,
  alpha: 0.4,
};

const POSE_WASM = "https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision@latest/wasm";
const POSE_MODEL =
  "https://storage.googleapis.com/mediapipe-models/pose_landmarker/pose_landmarker_heavy/float16/latest/pose_landmarker_heavy.task";

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

interface Props {
  /** Callback when user wants to close the Balmain module. */
  onClose?: () => void;
  /** Initial garment index. */
  initialGarment?: number;
}

export default function DressMeInBalmain({ onClose, initialGarment = 0 }: Props) {
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const landmarkerRef = useRef<any>(null);
  const engineRef = useRef<PhysicsGarmentEngine | null>(null);
  const garmentImgRef = useRef<HTMLImageElement | null>(null);
  const rafRef = useRef<number>(0);
  const lastTimeRef = useRef<number>(0);

  const [phase, setPhase] = useState<"loading" | "scanning" | "fitting" | "error">("loading");
  const [currentIdx, setCurrentIdx] = useState(initialGarment);
  const [fitVerdict, setFitVerdict] = useState("");
  const [fitLabel, setFitLabel] = useState("Analyzing drape physics...");
  const [fitScore, setFitScore] = useState(0);
  const [showScience, setShowScience] = useState(false);
  const [usePhysics, setUsePhysics] = useState(true);

  const garment = BALMAIN_COLLECTION[currentIdx];

  // -------------------------------------------------------------------------
  // Initialize Camera + Pose
  // -------------------------------------------------------------------------
  useEffect(() => {
    let cancelled = false;

    async function init() {
      try {
        // Request camera
        const stream = await navigator.mediaDevices.getUserMedia({
          video: { facingMode: "user", width: { ideal: 1280 }, height: { ideal: 720 } },
          audio: false,
        });

        if (cancelled) {
          stream.getTracks().forEach((t) => t.stop());
          return;
        }

        const video = videoRef.current!;
        video.srcObject = stream;
        await video.play();

        // Load MediaPipe
        const vision = await import("@mediapipe/tasks-vision");
        const { PoseLandmarker, FilesetResolver } = vision;
        const fileset = await FilesetResolver.forVisionTasks(POSE_WASM);
        const landmarker = await PoseLandmarker.createFromOptions(fileset, {
          baseOptions: { modelAssetPath: POSE_MODEL, delegate: "GPU" },
          runningMode: "VIDEO",
          numPoses: 1,
          minPoseDetectionConfidence: 0.5,
          minTrackingConfidence: 0.5,
        });

        if (cancelled) return;
        landmarkerRef.current = landmarker;
        setPhase("scanning");

        // Transition to fitting after brief scan
        setTimeout(() => {
          if (!cancelled) setPhase("fitting");
        }, 1500);
      } catch (err) {
        console.error("[DressMeInBalmain] Init error:", err);
        if (!cancelled) setPhase("error");
      }
    }

    init();
    return () => {
      cancelled = true;
      cancelAnimationFrame(rafRef.current);
    };
  }, []);

  // -------------------------------------------------------------------------
  // Load garment texture + physics engine
  // -------------------------------------------------------------------------
  useEffect(() => {
    if (!garment) return;

    // Load image
    const img = new Image();
    img.crossOrigin = "anonymous";
    img.src = garment.imagePath;
    img.onload = () => {
      garmentImgRef.current = img;
    };

    // Initialize or update physics engine
    if (usePhysics) {
      if (!engineRef.current) {
        engineRef.current = new PhysicsGarmentEngine(garment.material, 14, 20);
      } else {
        engineRef.current.setMaterial(garment.material);
      }
    }

    // Track Balmain interaction
    mirrorDigitalMiddleware.onBalmainClick(fitLabel);
  }, [garment, usePhysics]);

  // -------------------------------------------------------------------------
  // Animation Loop
  // -------------------------------------------------------------------------
  const detect = useCallback(() => {
    const video = videoRef.current;
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

    const vw = video.videoWidth;
    const vh = video.videoHeight;
    if (canvas.width !== vw) canvas.width = vw;
    if (canvas.height !== vh) canvas.height = vh;

    // Delta time
    const now = performance.now();
    const dt = lastTimeRef.current ? Math.min((now - lastTimeRef.current) / 1000, 0.033) : 0.016;
    lastTimeRef.current = now;

    // Pose detection
    const result = landmarker.detectForVideo(video, now);

    // Draw mirrored video
    ctx.save();
    ctx.translate(vw, 0);
    ctx.scale(-1, 1);
    ctx.drawImage(video, 0, 0, vw, vh);
    ctx.restore();

    // Overlay garment
    if (result?.landmarks?.[0] && garmentImg && garment) {
      const landmarks: PoseLandmark[] = result.landmarks[0];

      // Compute fit
      const elasticity = computeElasticityRatio(landmarks);
      const verdict = fabricFitComparator(elasticity);
      const label = verdictToUiLabel(verdict);
      setFitVerdict(verdict);
      setFitLabel(label);
      setFitScore(Math.round(elasticity * 100));

      const glow = verdict === "aligned" ? GLOW_BALMAIN : null;

      if (usePhysics && engineRef.current) {
        // Physics-based rendering
        const updated = engineRef.current.update(landmarks, vw, vh, dt);
        if (updated) {
          engineRef.current.render(ctx, garmentImg, glow);
        }
      } else {
        // Fallback: static overlay renderer
        renderGarmentOnBody(
          ctx,
          garmentImg,
          landmarks,
          {
            shoulderWidthRatio: garment.shoulderWidthRatio,
            neckY: garment.neckY,
            compositeMode: "multiply",
            opacity: 0.93,
          },
          vw,
          vh,
          glow,
        );
      }
    }

    rafRef.current = requestAnimationFrame(detect);
  }, [garment, usePhysics]);

  useEffect(() => {
    if (phase === "fitting" || phase === "scanning") {
      rafRef.current = requestAnimationFrame(detect);
    }
    return () => cancelAnimationFrame(rafRef.current);
  }, [phase, detect]);

  // -------------------------------------------------------------------------
  // Navigation
  // -------------------------------------------------------------------------
  const nextGarment = () => {
    engineRef.current?.reset();
    setCurrentIdx((i) => (i + 1) % BALMAIN_COLLECTION.length);
  };

  const prevGarment = () => {
    engineRef.current?.reset();
    setCurrentIdx((i) => (i - 1 + BALMAIN_COLLECTION.length) % BALMAIN_COLLECTION.length);
  };

  // -------------------------------------------------------------------------
  // Render
  // -------------------------------------------------------------------------
  return (
    <div style={styles.container}>
      {/* Hidden video element */}
      <video
        ref={videoRef}
        playsInline
        muted
        style={{ position: "absolute", opacity: 0, pointerEvents: "none", width: 1, height: 1 }}
      />

      {/* Main canvas */}
      <canvas ref={canvasRef} style={styles.canvas} />

      {/* Phase overlays */}
      <AnimatePresence>
        {phase === "loading" && (
          <motion.div
            key="loading"
            style={styles.overlay}
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
          >
            <div style={styles.loadingPulse} />
            <p style={styles.loadingText}>BALMAIN × TRYONYOU</p>
            <p style={styles.loadingSubtext}>Initializing Pose Intelligence...</p>
          </motion.div>
        )}

        {phase === "scanning" && (
          <motion.div
            key="scanning"
            style={styles.overlay}
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0, filter: "blur(12px)" }}
            transition={{ exit: { duration: 0.8 } }}
          >
            <div style={styles.scanLine} />
            <p style={styles.loadingText}>Body Geometry Detected</p>
            <p style={styles.loadingSubtext}>Mapping fabric physics to your silhouette...</p>
          </motion.div>
        )}

        {phase === "error" && (
          <motion.div key="error" style={styles.overlay} initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
            <p style={styles.loadingText}>Camera Access Required</p>
            <p style={styles.loadingSubtext}>
              Please allow camera access to experience the virtual fitting.
            </p>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Header */}
      <div style={styles.header}>
        <div style={styles.headerLeft}>
          <h2 style={styles.brandTitle}>BALMAIN</h2>
          <span style={styles.brandSub}>× TRYONYOU</span>
        </div>
        {onClose && (
          <button onClick={onClose} style={styles.closeBtn} aria-label="Close Balmain module">
            ✕
          </button>
        )}
      </div>

      {/* Bottom Panel */}
      {phase === "fitting" && (
        <motion.div
          style={styles.bottomPanel}
          initial={{ y: 60, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ delay: 0.3, duration: 0.6, ease: [0.23, 1, 0.32, 1] }}
        >
          {/* Garment Info */}
          <div style={styles.garmentInfo}>
            <h3 style={styles.garmentName}>{garment.name}</h3>
            <p style={styles.garmentCollection}>{garment.collection}</p>
            <p style={styles.garmentPrice}>€{garment.priceEur.toLocaleString("fr-FR")}</p>
          </div>

          {/* Fit Feedback */}
          <div style={styles.fitRow}>
            <div
              style={{
                ...styles.fitBadge,
                borderColor: fitVerdict === "aligned" ? "#D4AF37" : "#8B7E6A",
                boxShadow: fitVerdict === "aligned" ? "0 0 12px rgba(212,175,55,0.3)" : "none",
              }}
            >
              <span style={styles.fitLabel}>{fitLabel}</span>
              <span style={styles.fitScore}>{fitScore}%</span>
            </div>
            <button
              onClick={() => setShowScience(!showScience)}
              style={styles.scienceToggle}
              aria-label="Toggle fabric science"
            >
              {showScience ? "Hide Science" : "Fabric Science"}
            </button>
            <button
              onClick={() => setUsePhysics(!usePhysics)}
              style={{
                ...styles.scienceToggle,
                borderColor: usePhysics ? "#D4AF37" : "#555",
              }}
            >
              {usePhysics ? "Physics: ON" : "Physics: OFF"}
            </button>
          </div>

          {/* Fabric Science Panel */}
          <AnimatePresence>
            {showScience && (
              <motion.div
                style={styles.sciencePanel}
                initial={{ height: 0, opacity: 0 }}
                animate={{ height: "auto", opacity: 1 }}
                exit={{ height: 0, opacity: 0 }}
                transition={{ duration: 0.3 }}
              >
                <p style={styles.scienceTitle}>Fabric Physics — {garment.material.name}</p>
                <p style={styles.scienceText}>{garment.fabricScience}</p>
                <div style={styles.scienceGrid}>
                  <ScienceStat label="Structural" value={garment.material.structuralStiffness} />
                  <ScienceStat label="Shear" value={garment.material.shearStiffness} />
                  <ScienceStat label="Bend" value={garment.material.bendStiffness} />
                  <ScienceStat label="Mass" value={garment.material.particleMass / 2} />
                  <ScienceStat label="Damping" value={garment.material.damping} />
                  <ScienceStat label="Gravity" value={garment.material.gravityScale} />
                </div>
              </motion.div>
            )}
          </AnimatePresence>

          {/* Navigation */}
          <div style={styles.navRow}>
            <button onClick={prevGarment} style={styles.navBtn} aria-label="Previous garment">
              ← Previous
            </button>
            <span style={styles.navCounter}>
              {currentIdx + 1} / {BALMAIN_COLLECTION.length}
            </span>
            <button onClick={nextGarment} style={styles.navBtn} aria-label="Next garment">
              Next →
            </button>
          </div>
        </motion.div>
      )}

      {/* Inline styles for animations */}
      <style>{`
        @keyframes balmainScan {
          0% { transform: translateY(-100px); opacity: 0.4; }
          50% { transform: translateY(100px); opacity: 1; }
          100% { transform: translateY(-100px); opacity: 0.4; }
        }
        @keyframes balmainPulse {
          0%, 100% { box-shadow: 0 0 20px rgba(212,175,55,0.3); }
          50% { box-shadow: 0 0 40px rgba(212,175,55,0.6); }
        }
      `}</style>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Sub-components
// ---------------------------------------------------------------------------

function ScienceStat({ label, value }: { label: string; value: number }) {
  const pct = Math.round(value * 100);
  return (
    <div style={styles.scienceStatItem}>
      <span style={styles.scienceStatLabel}>{label}</span>
      <div style={styles.scienceStatBar}>
        <div style={{ ...styles.scienceStatFill, width: `${pct}%` }} />
      </div>
      <span style={styles.scienceStatValue}>{pct}%</span>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Styles
// ---------------------------------------------------------------------------

const styles: Record<string, React.CSSProperties> = {
  container: {
    position: "relative",
    width: "100%",
    maxWidth: 720,
    margin: "0 auto",
    borderRadius: 16,
    overflow: "hidden",
    backgroundColor: "#0A0806",
    border: "1px solid rgba(212,175,55,0.3)",
    aspectRatio: "16/10",
  },
  canvas: {
    width: "100%",
    height: "100%",
    display: "block",
    objectFit: "cover",
  },
  overlay: {
    position: "absolute",
    inset: 0,
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
    justifyContent: "center",
    backgroundColor: "rgba(10, 8, 6, 0.88)",
    backdropFilter: "blur(10px)",
    zIndex: 10,
  },
  loadingPulse: {
    width: 80,
    height: 80,
    borderRadius: "50%",
    border: "2px solid #D4AF37",
    animation: "balmainPulse 2s infinite",
    marginBottom: 24,
  },
  loadingText: {
    color: "#D4AF37",
    fontSize: 16,
    fontWeight: 600,
    letterSpacing: 4,
    textTransform: "uppercase" as const,
    margin: 0,
  },
  loadingSubtext: {
    color: "#8B7E6A",
    fontSize: 11,
    letterSpacing: 1.5,
    marginTop: 10,
    textTransform: "uppercase" as const,
  },
  scanLine: {
    width: "60%",
    height: 2,
    backgroundColor: "#D4AF37",
    boxShadow: "0 0 15px #D4AF37",
    animation: "balmainScan 2s infinite",
    marginBottom: 24,
  },
  header: {
    position: "absolute",
    top: 0,
    left: 0,
    right: 0,
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    padding: "16px 20px",
    background: "linear-gradient(rgba(10,8,6,0.7), transparent)",
    zIndex: 5,
  },
  headerLeft: {
    display: "flex",
    alignItems: "baseline",
    gap: 8,
  },
  brandTitle: {
    margin: 0,
    fontSize: 18,
    fontWeight: 700,
    letterSpacing: 6,
    color: "#FFFFFF",
    textTransform: "uppercase" as const,
  },
  brandSub: {
    fontSize: 10,
    letterSpacing: 2,
    color: "#D4AF37",
    textTransform: "uppercase" as const,
  },
  closeBtn: {
    background: "rgba(255,255,255,0.1)",
    border: "1px solid rgba(255,255,255,0.2)",
    color: "#FFF",
    width: 32,
    height: 32,
    borderRadius: "50%",
    fontSize: 14,
    cursor: "pointer",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
  },
  bottomPanel: {
    position: "absolute",
    bottom: 0,
    left: 0,
    right: 0,
    padding: "20px 20px 16px",
    background: "linear-gradient(transparent, rgba(10,8,6,0.95) 30%)",
    zIndex: 5,
  },
  garmentInfo: {
    marginBottom: 10,
  },
  garmentName: {
    margin: 0,
    fontSize: 15,
    fontWeight: 600,
    color: "#FFFFFF",
    letterSpacing: 0.5,
  },
  garmentCollection: {
    margin: "3px 0 0",
    fontSize: 10,
    color: "#D4AF37",
    letterSpacing: 2,
    textTransform: "uppercase" as const,
  },
  garmentPrice: {
    margin: "4px 0 0",
    fontSize: 13,
    color: "#8B7E6A",
    fontWeight: 500,
  },
  fitRow: {
    display: "flex",
    alignItems: "center",
    gap: 10,
    marginBottom: 10,
    flexWrap: "wrap" as const,
  },
  fitBadge: {
    display: "flex",
    alignItems: "center",
    gap: 8,
    padding: "5px 12px",
    borderRadius: 999,
    border: "1px solid #8B7E6A",
    backgroundColor: "rgba(0,0,0,0.4)",
  },
  fitLabel: {
    fontSize: 10,
    color: "#F5EFE6",
    letterSpacing: 1,
    textTransform: "uppercase" as const,
  },
  fitScore: {
    fontSize: 11,
    color: "#D4AF37",
    fontWeight: 700,
  },
  scienceToggle: {
    padding: "5px 12px",
    borderRadius: 999,
    border: "1px solid #555",
    backgroundColor: "transparent",
    color: "#D4AF37",
    fontSize: 9,
    letterSpacing: 1.5,
    textTransform: "uppercase" as const,
    cursor: "pointer",
  },
  sciencePanel: {
    overflow: "hidden",
    marginBottom: 10,
    padding: "10px 0",
    borderTop: "1px solid rgba(212,175,55,0.2)",
  },
  scienceTitle: {
    margin: "0 0 6px",
    fontSize: 10,
    color: "#D4AF37",
    letterSpacing: 2,
    textTransform: "uppercase" as const,
    fontWeight: 600,
  },
  scienceText: {
    margin: "0 0 10px",
    fontSize: 11,
    color: "#A89A86",
    lineHeight: 1.5,
  },
  scienceGrid: {
    display: "grid",
    gridTemplateColumns: "repeat(3, 1fr)",
    gap: 8,
  },
  scienceStatItem: {
    display: "flex",
    flexDirection: "column" as const,
    gap: 3,
  },
  scienceStatLabel: {
    fontSize: 8,
    color: "#8B7E6A",
    letterSpacing: 1,
    textTransform: "uppercase" as const,
  },
  scienceStatBar: {
    height: 3,
    backgroundColor: "rgba(255,255,255,0.1)",
    borderRadius: 2,
    overflow: "hidden",
  },
  scienceStatFill: {
    height: "100%",
    backgroundColor: "#D4AF37",
    borderRadius: 2,
    transition: "width 0.4s ease-out",
  },
  scienceStatValue: {
    fontSize: 9,
    color: "#F5EFE6",
    fontWeight: 600,
  },
  navRow: {
    display: "flex",
    alignItems: "center",
    justifyContent: "space-between",
    gap: 12,
  },
  navBtn: {
    padding: "8px 18px",
    borderRadius: 999,
    border: "none",
    backgroundColor: "#D4AF37",
    color: "#0A0806",
    fontSize: 10,
    fontWeight: 700,
    letterSpacing: 1.5,
    textTransform: "uppercase" as const,
    cursor: "pointer",
  },
  navCounter: {
    fontSize: 11,
    color: "#8B7E6A",
    letterSpacing: 1,
  },
};
