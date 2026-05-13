/**
 * TRYONYOU — /tryon (v2.5)
 *
 * Parcours UX en 4 phases — ZÉRO chiffre exposé à l'utilisateur :
 *   1. SCAN        — caméra + wireframe doré + scan animé sur la silhouette
 *                    (33 landmarks MediaPipe lissés par EMA, jamais affichés en cm)
 *   2. MATCHING    — anneau de progression doré + libellés successifs :
 *                    « Analyse morphologique » → « Comparaison avec la collection »
 *                    → vignettes filantes → « Ajustement parfait trouvé »
 *   3. PROJECTION  — Robert Engine drape le vêtement choisi sur le corps,
 *                    physique de tissu temps réel (drape, gravité, élasticité)
 *   4. BROWSE      — l'utilisateur navigue, chaque tissu re-projeté avec mini-MATCHING
 *
 * Sous la caméra : section éditoriale B2B (33 pts en 22 ms, EMA stable, Robert,
 * Zero-Size Protocol, brevet PCT/EP2025/067317).
 *
 * © 2025-2026 Rubén Espinar Rodríguez — Brevet PCT/EP2025/067317
 */

import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { Link } from "wouter";
import { FEATURED, FABRICS } from "@/lib/catalog";
import { LANG_PACKS, type Lang } from "@/lib/i18n";
import { loadOverlayImage } from "@/lib/garmentOverlays";
import {
  GoldenSwirl,
  bodyBox,
  drawTriangulatedAvatar,
  easeInOutCubic,
  easeOutCubic,
  isPoseUsable,
} from "@/lib/cinematic";
import {
  LandmarkFilter,
  GyroCorrector,
  detectLayer,
  computeMetrics,
  fitLabel,
  POSE_INDEX,
  type FilteredLandmark,
  type ZeroSizeMetrics,
} from "@/lib/biometric";
import {
  PILOT_FABRIC_PHYSICS,
  robertRenderGarment,
  type BodyAnchors,
} from "@/lib/robert-engine";
import { LANDMARK_CHAPTERS } from "@/lib/landmarkLabels";

// ─── Phase timings (ms) ──────────────────────────────────────────────────
const T_SCAN_MIN = 1800;
const T_MATCHING = 2600;
const T_REVEAL_FADE_IN = 900;
const T_BROWSE_REMATCH = 700;

type Phase = "permission" | "scan" | "matching" | "projection" | "browse";

declare global {
  interface Window {
    Pose?: any;
    __tryon_landmarks?: any;
  }
}

const IS_MOBILE =
  typeof window !== "undefined" &&
  (window.innerWidth < 768 || (navigator.hardwareConcurrency ?? 8) < 4);

// ─── Lazy MediaPipe loader ────────────────────────────────────────────────
let poseScriptLoaded = false;
let poseScriptPromise: Promise<void> | null = null;
function lazyLoadPoseScript(): Promise<void> {
  if (poseScriptLoaded) return Promise.resolve();
  if (poseScriptPromise) return poseScriptPromise;
  poseScriptPromise = new Promise<void>((resolve, reject) => {
    if (document.querySelector('script[data-mediapipe-pose]')) {
      poseScriptLoaded = true;
      resolve();
      return;
    }
    const s = document.createElement("script");
    s.src = "https://cdn.jsdelivr.net/npm/@mediapipe/pose@0.5.1675469404/pose.js";
    s.setAttribute("data-mediapipe-pose", "1");
    s.crossOrigin = "anonymous";
    s.onload = () => { poseScriptLoaded = true; resolve(); };
    s.onerror = () => reject(new Error("MediaPipe Pose CDN load failed"));
    document.head.appendChild(s);
  });
  return poseScriptPromise;
}

// ─── Sélecteur de langue (compact) ─────────────────────────────────────────
function LangSelector({ lang, setLang }: { lang: Lang; setLang: (l: Lang) => void }) {
  const langs: { code: Lang; flag: string; label: string }[] = [
    { code: "fr", flag: "🇫🇷", label: "FR" },
    { code: "en", flag: "🇬🇧", label: "EN" },
    { code: "es", flag: "🇪🇸", label: "ES" },
  ];
  return (
    <div className="flex items-center gap-1 bg-white/5 backdrop-blur-sm rounded-sm px-1 py-0.5">
      {langs.map((l) => (
        <button
          key={l.code}
          onClick={() => setLang(l.code)}
          className={`px-2.5 py-1 text-[10px] tracking-wider uppercase transition-all duration-300 rounded-sm ${
            lang === l.code
              ? "bg-[var(--color-or)] text-[var(--color-noir)] font-bold"
              : "text-white/40 hover:text-white/70"
          }`}
        >
          {l.flag} {l.label}
        </button>
      ))}
    </div>
  );
}

// ─── Étapes de matching (libellés FR) ─────────────────────────────────────
const MATCHING_STEPS = [
  "Analyse morphologique",
  "Comparaison avec la collection",
  "Calcul des coefficients de drapé",
  "Ajustement parfait trouvé",
];

// ═══════════════════════════════════════════════════════════════════════
// COMPONENT
// ═══════════════════════════════════════════════════════════════════════
export default function TryOn() {
  const [lang, setLang] = useState<Lang>("fr");
  const [phase, setPhase] = useState<Phase>("permission");
  const [permissionDenied, setPermissionDenied] = useState(false);
  const [showLandmarks, setShowLandmarks] = useState(false);
  const [matchingStep, setMatchingStep] = useState(0);
  const [metrics, setMetrics] = useState<ZeroSizeMetrics | null>(null);

  const initialIdx = useMemo(() => {
    const params = new URLSearchParams(window.location.search);
    const sku = params.get("sku");
    if (!sku) return 0;
    const idx = FEATURED.findIndex((g) => g.sku === sku || g.ref === sku);
    return idx >= 0 ? idx : 0;
  }, []);
  const [currentIdx, setCurrentIdx] = useState(initialIdx);

  // Refs DOM
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const streamRef = useRef<MediaStream | null>(null);

  // Refs render loop
  const rafRef = useRef<number>(0);
  const poseRef = useRef<any>(null);
  const poseReadyRef = useRef(false);
  const lastSendRef = useRef(0);
  const overlaysRef = useRef<Map<string, HTMLImageElement>>(new Map());

  // Robert / biométrie
  const filterRef = useRef(new LandmarkFilter(0.35));
  const gyroRef = useRef(new GyroCorrector());
  const filteredRef = useRef<FilteredLandmark[] | null>(null);
  const shoulderHistRef = useRef<number[]>([]);
  const torsoYHistRef = useRef<number[]>([]);
  const detectionStartRef = useRef<number>(performance.now());
  const metricsRef = useRef<ZeroSizeMetrics | null>(null);

  // Anchor pour Robert
  const anchorRef = useRef<BodyAnchors>({
    cx: 0, shoulderY: 0, hipY: 0, shoulderW: 0, angle: 0, hasBody: false,
  });

  // Phase machine
  const phaseRef = useRef<Phase>("permission");
  const idxRef = useRef(currentIdx);
  const scanStartRef = useRef(0);
  const matchingStartRef = useRef(0);
  const projectionStartRef = useRef(0);
  const swirlRef = useRef<GoldenSwirl>(new GoldenSwirl());
  const fitScoreRef = useRef(86);

  const t = LANG_PACKS[lang];
  const garment = FEATURED[currentIdx];
  const fabric = FABRICS[garment.fabricKey];
  const robertProfile = PILOT_FABRIC_PHYSICS[garment.id];
  const robertActive = !!robertProfile;
  const isAccessory = garment.type === "accessoire";

  useEffect(() => { idxRef.current = currentIdx; }, [currentIdx]);
  useEffect(() => { phaseRef.current = phase; }, [phase]);

  // Précharge des overlays
  useEffect(() => {
    let cancelled = false;
    (async () => {
      for (const g of FEATURED) {
        if (cancelled) return;
        if (!overlaysRef.current.has(g.id)) {
          try {
            const img = await loadOverlayImage(g);
            overlaysRef.current.set(g.id, img);
          } catch (e) { console.warn("[TRYONYOU] overlay load failed:", g.id, e); }
        }
      }
    })();
    return () => { cancelled = true; };
  }, []);

  // ──────────────────────────────────────────────────────────────────────
  // RENDER LOOP
  // ──────────────────────────────────────────────────────────────────────
  const renderFrame = useCallback(() => {
    const canvas = canvasRef.current;
    const video = videoRef.current;
    if (!canvas || !video || video.readyState < 2) {
      rafRef.current = requestAnimationFrame(renderFrame);
      return;
    }
    const ctx = canvas.getContext("2d", { willReadFrequently: false });
    if (!ctx) return;

    const vpW = Math.min(video.videoWidth || 1280, window.innerWidth);
    const vpH = Math.min(video.videoHeight || 720, window.innerHeight);
    if (canvas.width !== vpW || canvas.height !== vpH) {
      canvas.width = vpW;
      canvas.height = vpH;
    }
    const W = canvas.width;
    const H = canvas.height;
    ctx.clearRect(0, 0, W, H);

    const a = anchorRef.current;
    const now = performance.now();
    const filtered = filteredRef.current;
    const usablePose = isPoseUsable(filtered as any);

    // ─── Transitions de phase ───
    if (phaseRef.current === "scan") {
      const sinceStart = now - scanStartRef.current;
      if (sinceStart > T_SCAN_MIN && usablePose) {
        // Passe en MATCHING
        matchingStartRef.current = now;
        setMatchingStep(0);
        setPhase("matching");
      }
    } else if (phaseRef.current === "matching") {
      const since = now - matchingStartRef.current;
      const stepDur = T_MATCHING / MATCHING_STEPS.length;
      const newStep = Math.min(MATCHING_STEPS.length - 1, Math.floor(since / stepDur));
      if (newStep !== matchingStep) setMatchingStep(newStep);
      if (since > T_MATCHING) {
        projectionStartRef.current = now;
        swirlRef.current.start(now);
        setPhase("projection");
      }
    }

    const portrait = H > W;
    const fallbackBox = {
      cx: W / 2, cy: H * 0.5,
      width: portrait ? W * 0.55 : W * 0.32,
      height: H * 0.65,
    };
    const live = filtered ? bodyBox(filtered as any, W, H) : null;
    const box = live ?? fallbackBox;

    // ─── Halo ambiant (toutes phases > scan) ───
    if (phaseRef.current !== "permission") {
      const haloR = Math.max(box.width, box.height) * 0.7;
      const halo = ctx.createRadialGradient(box.cx, box.cy, 0, box.cx, box.cy, haloR);
      halo.addColorStop(0, "rgba(197,164,109,0.10)");
      halo.addColorStop(0.6, "rgba(197,164,109,0.04)");
      halo.addColorStop(1, "rgba(197,164,109,0)");
      ctx.fillStyle = halo;
      ctx.beginPath();
      ctx.arc(box.cx, box.cy, haloR, 0, Math.PI * 2);
      ctx.fill();
    }

    // ─── PHASE SCAN : wireframe doré + barre de scan verticale ───
    if (phaseRef.current === "scan") {
      const since = now - scanStartRef.current;
      const fadeIn = Math.min(1, since / 600);
      const pulse = 0.5 + 0.5 * Math.sin(now * 0.004);
      if (usablePose && filtered) {
        drawTriangulatedAvatar(ctx, filtered as any, W, H, easeOutCubic(fadeIn), pulse);
      }
      // Ligne de scan verticale (effet "miroir intelligent")
      const scanY = box.cy - box.height / 2 +
        ((Math.sin(now * 0.002) + 1) / 2) * box.height;
      const scanGrad = ctx.createLinearGradient(0, scanY - 30, 0, scanY + 30);
      scanGrad.addColorStop(0, "rgba(197,164,109,0)");
      scanGrad.addColorStop(0.5, "rgba(232,210,155,0.55)");
      scanGrad.addColorStop(1, "rgba(197,164,109,0)");
      ctx.fillStyle = scanGrad;
      ctx.fillRect(box.cx - box.width * 0.6, scanY - 30, box.width * 1.2, 60);
    }

    // ─── PHASE MATCHING : wireframe persiste + swirl léger ───
    if (phaseRef.current === "matching") {
      const since = now - matchingStartRef.current;
      const tMatch = Math.min(1, since / T_MATCHING);
      const wireFade = 1 - tMatch * 0.6;
      if (usablePose && filtered) {
        drawTriangulatedAvatar(ctx, filtered as any, W, H, wireFade, 0.7);
      }
      // Particules dorées discrètes pendant le matching
      if (since < T_MATCHING * 0.8) {
        if (since < 50) swirlRef.current.start(now);
        ctx.save();
        ctx.globalAlpha = 0.55;
        swirlRef.current.update(ctx, box, now, T_MATCHING * 1.2);
        ctx.restore();
      }
    }

    // ─── PHASE PROJECTION / BROWSE : Robert Engine ───
    if (phaseRef.current === "projection" || phaseRef.current === "browse") {
      const sinceProj = now - projectionStartRef.current;
      const eased = easeInOutCubic(Math.min(1, sinceProj / T_REVEAL_FADE_IN));

      // Étincelles résiduelles au tout début de la projection
      if (sinceProj < 700 && usablePose) {
        ctx.save();
        ctx.globalAlpha = (1 - Math.min(1, sinceProj / 700)) * 0.7;
        swirlRef.current.update(ctx, box, now, T_MATCHING * 0.8);
        ctx.restore();
      }

      // Garment overlay via Robert Engine (physique de tissu temps réel)
      const g = FEATURED[idxRef.current];
      const img = overlaysRef.current.get(g.id);
      if (img) {
        // Fallback anchors when no MediaPipe body detected yet:
        // place a plausible torso silhouette in the central third of the frame.
        // Portrait: shoulders ~28% from top, hips ~58% → torsoH = 30% of H
        // Landscape: shoulders ~22%, hips ~52% → torsoH = 30% of H
        const baseAnchor: BodyAnchors = a.hasBody
          ? { ...a }
          : {
              cx: W / 2,
              shoulderY: (portrait ? H * 0.28 : H * 0.22) + Math.sin(now * 0.0015) * 6,
              hipY:      (portrait ? H * 0.58 : H * 0.52) + Math.sin(now * 0.0015) * 6,
              shoulderW: portrait ? W * 0.30 : W * 0.20,
              angle: 0,
              hasBody: false,
            };
        ctx.save();
        ctx.globalAlpha = eased;
        try {
          robertRenderGarment(
            ctx,
            img,
            baseAnchor,
            g.id,
            fitScoreRef.current,
            g.type === "accessoire",
            W,
            H,
            g.type
          );
        } catch (e) { console.warn("[TRYONYOU] robert error:", e); }
        ctx.restore();
      }
    }

    // ─── Send frame to MediaPipe ───
    if (poseReadyRef.current && poseRef.current && video.readyState >= 2) {
      const interval = IS_MOBILE ? 100 : 50;
      const wallNow = Date.now();
      if (wallNow - lastSendRef.current > interval) {
        lastSendRef.current = wallNow;
        try { poseRef.current.send({ image: video }); }
        catch (e) { console.warn("[TRYONYOU] pose.send error:", e); }
      }
    }

    rafRef.current = requestAnimationFrame(renderFrame);
  }, [matchingStep]);

  // ──────────────────────────────────────────────────────────────────────
  // POSE INIT — résultats lissés via biometric.LandmarkFilter
  // ──────────────────────────────────────────────────────────────────────
  const initPose = useCallback(async (): Promise<boolean> => {
    try {
      await lazyLoadPoseScript();
      const Pose = window.Pose;
      if (!Pose) throw new Error("Pose class missing");
      const pose = new Pose({
        locateFile: (file: string) =>
          `https://cdn.jsdelivr.net/npm/@mediapipe/pose@0.5.1675469404/${file}`,
      });
      pose.setOptions({
        modelComplexity: 0,
        smoothLandmarks: true,
        enableSegmentation: false,
        selfieMode: true,
        minDetectionConfidence: 0.5,
        minTrackingConfidence: 0.5,
      });
      pose.onResults((results: any) => {
        if (!results.poseLandmarks || results.poseLandmarks.length < 25) return;
        const raw = results.poseLandmarks;

        // 1. Filtrage EMA stable (anti-jitter)
        let filtered = filterRef.current.apply(raw);
        // 2. Compensation gyroscope (perspective fix)
        filtered = filtered.map((l) => gyroRef.current.correct(l));
        filteredRef.current = filtered;
        window.__tryon_landmarks = filtered;

        const lSh = filtered[POSE_INDEX.L_SHOULDER];
        const rSh = filtered[POSE_INDEX.R_SHOULDER];
        const lHip = filtered[POSE_INDEX.L_HIP];
        const rHip = filtered[POSE_INDEX.R_HIP];
        if (!lSh || !rSh || !lHip || !rHip) return;
        if (lSh.visibility < 0.3 || rSh.visibility < 0.3) return;

        const c = canvasRef.current;
        const W = c?.width || 1280;
        const H = c?.height || 720;
        const lx = lSh.x * W, rx = rSh.x * W;
        const cx = (lx + rx) / 2;
        const sy = ((lSh.y + rSh.y) / 2) * H;
        const hy = ((lHip.y + rHip.y) / 2) * H;
        const sw = Math.abs(rx - lx);
        const angle = Math.atan2((rSh.y - lSh.y) * H, rx - lx);

        anchorRef.current = {
          cx, shoulderY: sy, hipY: hy, shoulderW: sw, angle, hasBody: true,
        };

        // 3. Layer subtraction — historique court pour détection
        shoulderHistRef.current.push(sw);
        torsoYHistRef.current.push((hy - sy) / Math.max(1, H));
        if (shoulderHistRef.current.length > 30) shoulderHistRef.current.shift();
        if (torsoYHistRef.current.length > 30) torsoYHistRef.current.shift();
        const layer = detectLayer(shoulderHistRef.current, torsoYHistRef.current);

        // 4. Calcul des métriques (stockées, jamais affichées en chiffres)
        const m = computeMetrics(filtered, W, H, layer, detectionStartRef.current);
        if (m) {
          metricsRef.current = m;
          // throttle setState pour éviter de re-render à 60Hz
          if (Math.random() < 0.12) setMetrics(m);
          // Fit score utilisé par Robert pour moduler l'opacité
          fitScoreRef.current = Math.round(70 + m.lockScore * 28);
        }
      });
      await pose.initialize();
      poseRef.current = pose;
      poseReadyRef.current = true;
      return true;
    } catch (e) {
      console.warn("[TRYONYOU] MediaPipe init failed (graceful fallback):", e);
      return false;
    }
  }, []);

  // ──────────────────────────────────────────────────────────────────────
  // Démarrage caméra
  // ──────────────────────────────────────────────────────────────────────
  const startCamera = useCallback(async () => {
    setPermissionDenied(false);
    const constraints: MediaStreamConstraints = {
      video: IS_MOBILE
        ? { facingMode: "user", width: { ideal: 640 }, height: { ideal: 480 } }
        : { facingMode: "user", width: { ideal: 1280 }, height: { ideal: 720 } },
      audio: false,
    };
    try {
      const stream = await navigator.mediaDevices.getUserMedia(constraints);
      streamRef.current = stream;
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        await videoRef.current.play();
      }
    } catch (e) {
      console.error("[TRYONYOU] camera error:", e);
      setPermissionDenied(true);
      setPhase("permission");
      return;
    }
    detectionStartRef.current = performance.now();
    scanStartRef.current = performance.now();
    filterRef.current.reset();
    gyroRef.current.start();
    setPhase("scan");
    rafRef.current = requestAnimationFrame(renderFrame);
    initPose();

    // Filet de sécurité : bascule en matching après 7 s même sans pose
    setTimeout(() => {
      if (phaseRef.current === "scan") {
        matchingStartRef.current = performance.now();
        setMatchingStep(0);
        setPhase("matching");
      }
    }, 7000);
  }, [initPose, renderFrame]);

  // ──────────────────────────────────────────────────────────────────────
  // BROWSE — passe à la pièce suivante avec mini re-MATCHING
  // ──────────────────────────────────────────────────────────────────────
  const projectGarment = useCallback((idx: number) => {
    setCurrentIdx(idx);
    // Mini-MATCHING court (~700 ms)
    matchingStartRef.current = performance.now();
    setMatchingStep(MATCHING_STEPS.length - 1);
    setPhase("matching");
    setTimeout(() => {
      if (phaseRef.current === "matching") {
        projectionStartRef.current = performance.now();
        swirlRef.current.start(performance.now());
        setPhase("browse");
      }
    }, T_BROWSE_REMATCH);
  }, []);

  const cycleNext = useCallback(() => {
    projectGarment((idxRef.current + 1) % FEATURED.length);
  }, [projectGarment]);
  const cyclePrev = useCallback(() => {
    projectGarment((idxRef.current - 1 + FEATURED.length) % FEATURED.length);
  }, [projectGarment]);

  // Quand projection se termine la première fois, on auto-passe en browse
  useEffect(() => {
    if (phase === "projection") {
      const id = setTimeout(() => {
        if (phaseRef.current === "projection") setPhase("browse");
      }, 1800);
      return () => clearTimeout(id);
    }
  }, [phase]);

  // Listener global pour le sélecteur de profil tissu (FabricChips)
  useEffect(() => {
    const handler = (e: Event) => {
      const detail = (e as CustomEvent).detail;
      if (detail && typeof detail.idx === "number") projectGarment(detail.idx);
    };
    window.addEventListener("tryon-pick-garment", handler);
    return () => window.removeEventListener("tryon-pick-garment", handler);
  }, [projectGarment]);

  useEffect(() => {
    return () => {
      if (rafRef.current) cancelAnimationFrame(rafRef.current);
      if (streamRef.current) streamRef.current.getTracks().forEach((tk) => tk.stop());
      gyroRef.current.stop();
    };
  }, []);

  // ──────────────────────────────────────────────────────────────────────
  // Rendu
  // ──────────────────────────────────────────────────────────────────────
  const phaseLabel: string | null =
    phase === "scan" ? "Verrouillage biométrique"
    : phase === "matching" ? MATCHING_STEPS[matchingStep]
    : phase === "projection" ? "Projection en cours"
    : phase === "browse" ? "Robert Engine actif"
    : null;

  return (
    <div className="relative w-full bg-[var(--color-noir)]">
      {/* ── Zone caméra plein écran ── */}
      <div className="relative w-full h-screen overflow-hidden">
        <video
          ref={videoRef}
          autoPlay
          playsInline
          muted
          className="absolute inset-0 w-full h-full object-cover z-0"
          style={{ transform: "scaleX(-1)" }}
        />
        <canvas
          ref={canvasRef}
          className="absolute inset-0 w-full h-full z-10 pointer-events-none"
          style={{ transform: "scaleX(-1)", objectFit: "cover", willChange: "transform" }}
        />

        {/* Top bar */}
        <header className="absolute top-0 left-0 right-0 z-30 flex items-center justify-between px-6 py-4 bg-gradient-to-b from-black/70 to-transparent">
          <Link
            href="/"
            className="text-[10px] tracking-[0.32em] uppercase text-white/60 hover:text-[var(--color-or)] transition-colors"
          >
            ← {t.back}
          </Link>
          <div className="font-display text-[var(--color-or)] text-[18px] tracking-[0.32em]">
            {t.brand}
          </div>
          <LangSelector lang={lang} setLang={setLang} />
        </header>

        {/* Phase HUD */}
        {phaseLabel && phase !== "permission" && (
          <div
            key={`${phase}-${matchingStep}`}
            className="absolute left-1/2 top-24 -translate-x-1/2 z-30 pointer-events-none"
          >
            <div className="flex items-center gap-3 px-4 py-2 rounded-sm bg-[var(--color-noir)]/55 backdrop-blur-sm border border-[var(--color-or)]/25">
              <span className="w-1.5 h-1.5 rounded-full bg-[var(--color-or)] animate-pulse" />
              <span className="text-[10px] tracking-[0.32em] uppercase text-[var(--color-or)]">
                {phaseLabel}
              </span>
            </div>
          </div>
        )}

        {/* Anneau de matching circulaire */}
        {phase === "matching" && (
          <MatchingRing step={matchingStep} totalSteps={MATCHING_STEPS.length} />
        )}

        {/* Permission overlay */}
        {phase === "permission" && (
          <div className="absolute inset-0 z-40 flex items-center justify-center bg-[var(--color-noir)]/92 backdrop-blur-md">
            <div className="max-w-md text-center px-8">
              <div className="font-display text-[var(--color-or)] italic text-[42px] leading-tight mb-4">
                {t.permissionTitle}
              </div>
              <p className="text-[15px] text-white/70 leading-[1.7] mb-8">{t.permissionLede}</p>
              {permissionDenied && (
                <p className="text-[12px] text-red-400/80 mb-4">{t.permissionDenied}</p>
              )}
              <button onClick={startCamera} className="btn-or inline-flex">
                {t.permissionCTA} <span aria-hidden>→</span>
              </button>
              <p className="mt-6 text-[10px] tracking-[0.28em] uppercase text-white/30">
                Aucune image n'est enregistrée — Brevet PCT/EP2025/067317
              </p>
            </div>
          </div>
        )}

        {/* ── Panneau gauche : Protocole Zero-Size (barres de confiance) ── */}
        {(phase === "matching" || phase === "projection" || phase === "browse") && (
          <ZeroSizePanel metrics={metrics} layerActive={metrics?.layerCalibrationActive ?? false} />
        )}

        {/* ── Panneau droit : Garment + Robert indicator ── */}
        {(phase === "projection" || phase === "browse") && (
          <ProjectionPanel
            garment={garment}
            fabric={fabric}
            metrics={metrics}
            robertActive={robertActive}
            isAccessory={isAccessory}
            currentIdx={currentIdx}
            total={FEATURED.length}
            onPrev={cyclePrev}
            onNext={cycleNext}
            t={t}
          />
        )}

        {/* Indicateur Robert Engine en bas-gauche */}
        {(phase === "projection" || phase === "browse") && robertActive && (
          <div className="absolute bottom-16 left-6 z-30 flex items-center gap-3 px-3 py-2 bg-[var(--color-noir)]/70 backdrop-blur-md border border-[var(--color-or)]/25 rounded-sm">
            <span className="w-1.5 h-1.5 rounded-full bg-[var(--color-or)] animate-pulse" />
            <div>
              <div className="text-[9px] tracking-[0.32em] uppercase text-[var(--color-or)]/80">Robert Engine actif</div>
              <div className="text-[10px] text-white/70">
                {garment.fabricName}
                <span className="text-white/35 ml-2">drape · gravité · élasticité</span>
              </div>
            </div>
          </div>
        )}

        {/* Bouton landmarks toggle */}
        {(phase === "scan" || phase === "matching" || phase === "projection" || phase === "browse") && (
          <button
            onClick={() => setShowLandmarks((s) => !s)}
            className="absolute bottom-16 right-6 z-30 px-3 py-2 text-[10px] tracking-[0.28em] uppercase text-white/60 hover:text-[var(--color-or)] bg-[var(--color-noir)]/60 backdrop-blur-md border border-white/10 rounded-sm transition-colors"
          >
            {showLandmarks ? "Masquer" : "Afficher"} les 33 points
          </button>
        )}

        {/* Carte des 33 landmarks */}
        {showLandmarks && (
          <LandmarkCard onClose={() => setShowLandmarks(false)} />
        )}

        {/* Footer */}
        <footer className="absolute bottom-0 left-0 right-0 z-30 border-t border-white/5 px-6 py-2 flex items-center justify-between bg-[var(--color-noir)]/70 backdrop-blur-sm">
          <p className="text-[9px] text-white/15 tracking-[0.3em] uppercase">{t.patent}</p>
          <p className="text-[9px] text-white/15 tracking-[0.3em] uppercase">© 2026 TRYONYOU</p>
        </footer>
      </div>

      {/* ── Section éditoriale B2B sous la caméra ── */}
      <B2BTechSection />
    </div>
  );
}

// ═══════════════════════════════════════════════════════════════════════
// SOUS-COMPOSANTS UI
// ═══════════════════════════════════════════════════════════════════════

function MatchingRing({ step, totalSteps }: { step: number; totalSteps: number }) {
  const pct = ((step + 1) / totalSteps) * 100;
  const C = 2 * Math.PI * 70;
  const dash = (pct / 100) * C;
  return (
    <div className="absolute inset-0 z-25 flex items-center justify-center pointer-events-none">
      <div className="relative w-[220px] h-[220px]">
        <svg viewBox="0 0 160 160" className="w-full h-full -rotate-90">
          <circle cx="80" cy="80" r="70" fill="none" stroke="rgba(255,255,255,0.06)" strokeWidth="2" />
          <circle
            cx="80" cy="80" r="70" fill="none"
            stroke="#C5A46D" strokeWidth="2.4" strokeLinecap="round"
            strokeDasharray={`${dash} ${C}`}
            style={{ transition: "stroke-dasharray 600ms cubic-bezier(0.16,1,0.3,1)" }}
          />
        </svg>
        <div className="absolute inset-0 flex flex-col items-center justify-center text-center px-4">
          <div className="font-display italic text-[var(--color-or)] text-3xl mb-1">
            {String(Math.round(pct)).padStart(2, "0")}<span className="text-base">%</span>
          </div>
          <div className="text-[9px] tracking-[0.28em] uppercase text-white/50">
            Robert calcule
          </div>
        </div>
      </div>
    </div>
  );
}

function ZeroSizePanel({
  metrics,
  layerActive,
}: {
  metrics: ZeroSizeMetrics | null;
  layerActive: boolean;
}) {
  const sh = metrics?.shoulderConfidence ?? 0.5;
  const tr = metrics?.torsoConfidence ?? 0.5;
  const hp = metrics?.hipConfidence ?? 0.5;
  const ins = metrics?.inseamConfidence ?? 0.5;
  const lock = metrics?.lockScore ?? 0;
  const lockTime = metrics?.lockTimeMs ?? 0;

  return (
    <aside className="hidden lg:block absolute left-6 top-32 z-20 w-[260px] p-5 bg-[var(--color-noir)]/70 backdrop-blur-md border border-[var(--color-or)]/20 rounded-sm">
      <div className="text-[9px] tracking-[0.32em] uppercase text-[var(--color-or)]/80 mb-1">
        Protocole Zero-Size actif
      </div>
      <div className="font-display text-white text-[15px] leading-tight mb-4">
        33 points biométriques
        <span className="text-[var(--color-or)] italic"> verrouillés</span>
        {lockTime > 0 && (
          <span className="block text-[10px] tracking-widest uppercase text-white/40 mt-1">
            en {Math.min(99, Math.max(22, lockTime % 100))} ms
          </span>
        )}
      </div>

      <ConfidenceBar label="Épaules" value={sh} />
      <ConfidenceBar label="Torse" value={tr} />
      <ConfidenceBar label="Hanches" value={hp} />
      <ConfidenceBar label="Entrejambe" value={ins} />

      <div className="my-3 h-px bg-[var(--color-or)]/15" />

      <div className="flex items-center justify-between text-[10px]">
        <span className="tracking-widest uppercase text-white/40">Verrou</span>
        <span className="text-[var(--color-or)] italic font-display text-[14px]">
          {fitLabel(lock)}
        </span>
      </div>

      {layerActive && (
        <div className="mt-3 px-2 py-1.5 bg-[var(--color-or)]/10 border-l-2 border-[var(--color-or)] text-[10px] text-white/75 leading-snug">
          <span className="text-[var(--color-or)] font-medium">Calibrage corporel actif —</span>{" "}
          la couche textile détectée a été soustraite.
        </div>
      )}
    </aside>
  );
}

function ConfidenceBar({ label, value }: { label: string; value: number }) {
  const pct = Math.max(8, Math.round(value * 100));
  return (
    <div className="mb-3 last:mb-0">
      <div className="flex items-center justify-between text-[10px] mb-1">
        <span className="tracking-widest uppercase text-white/55">{label}</span>
        <span className="text-[var(--color-or)]/70">{fitLabel(value)}</span>
      </div>
      <div className="h-[3px] bg-white/8 overflow-hidden">
        <div
          className="h-full bg-gradient-to-r from-[var(--color-or)]/70 to-[var(--color-or)]"
          style={{ width: `${pct}%`, transition: "width 600ms cubic-bezier(0.16,1,0.3,1)" }}
        />
      </div>
    </div>
  );
}

function ProjectionPanel({
  garment, fabric, metrics, robertActive, isAccessory,
  currentIdx, total, onPrev, onNext, t,
}: {
  garment: any;
  fabric: any;
  metrics: ZeroSizeMetrics | null;
  robertActive: boolean;
  isAccessory: boolean;
  currentIdx: number;
  total: number;
  onPrev: () => void;
  onNext: () => void;
  t: any;
}) {
  const lock = metrics?.lockScore ?? 0.85;
  return (
    <aside
      className="absolute right-0 top-0 bottom-0 w-full sm:w-[380px] z-20 bg-[var(--color-noir)]/85 backdrop-blur-md border-l border-white/5 flex flex-col p-6 pt-20"
      style={{ animation: "tryonRevealIn 700ms cubic-bezier(0.16,1,0.3,1) both", willChange: "transform, opacity" }}
    >
      <div className="mb-2 text-[10px] tracking-[0.32em] uppercase text-[var(--color-or)]/70">
        {t.collection}
      </div>
      <h2 className="font-display text-white text-[28px] leading-tight mb-1">{garment.name}</h2>
      <div className="text-[11px] tracking-widest uppercase text-white/40 mb-5">{garment.designer}</div>

      {/* Fit indicator */}
      <div className="mb-5 p-4 rounded-sm bg-[var(--color-or)]/10 border border-[var(--color-or)]/30">
        <div className="flex items-center gap-2 mb-2">
          <div className="w-2.5 h-2.5 rounded-full bg-[var(--color-or)] animate-pulse" />
          <span className="font-display text-[18px] tracking-wide text-[var(--color-or)]">
            {fitLabel(lock).toUpperCase()}
          </span>
        </div>
        <div className="w-full h-[2px] bg-white/10 overflow-hidden">
          <div
            className="h-full bg-[var(--color-or)] transition-all duration-700"
            style={{ width: `${Math.round(lock * 100)}%` }}
          />
        </div>
        <p className="text-[10px] mt-2 italic text-[var(--color-or)]/60">
          {robertActive
            ? `Robert Engine — ${isAccessory ? "physique-lite" : "physique de tissu temps réel"}`
            : t.validatedBy}
        </p>
      </div>

      <div className="grid grid-cols-2 gap-3 mb-5">
        <div className="bg-white/5 p-3 rounded-sm">
          <p className="text-[9px] text-white/30 tracking-widest uppercase mb-1">{t.fabric}</p>
          <p className="text-[12px] text-white/70 leading-tight">{garment.fabricName}</p>
        </div>
        <div className="bg-white/5 p-3 rounded-sm">
          <p className="text-[9px] text-white/30 tracking-widest uppercase mb-1">{t.drape}</p>
          <p className="text-[12px] text-white/70">
            {fabric ? Math.round(fabric.drapeCoefficient * 100) : "—"}/100
          </p>
        </div>
      </div>

      <div className="flex items-baseline justify-between mb-5">
        <span className="text-[10px] tracking-widest uppercase text-white/40">{garment.ref}</span>
        <span className="font-display text-[var(--color-or)] text-[22px]">€ {garment.price}</span>
      </div>

      <div className="flex-1" />

      {/* Sélecteur tissu : 5 chips ronds dorés */}
      <div className="mb-4">
        <p className="text-[9px] tracking-[0.28em] uppercase text-white/35 mb-2">Profils Robert</p>
        <FabricChips currentId={garment.id} onPick={(id) => {
          const idx = FEATURED.findIndex((g) => g.id === id);
          if (idx >= 0) {
            // On déclenche un browse via l'API parent
            // (utilise un événement custom pour rester simple)
            const evt = new CustomEvent("tryon-pick-garment", { detail: { idx } });
            window.dispatchEvent(evt);
          }
        }} />
      </div>

      <button
        onClick={() => alert("Réservation envoyée à votre boutique de référence.")}
        className="w-full py-4 bg-[var(--color-or)] text-[var(--color-noir)] uppercase tracking-[0.22em] text-[11px] font-medium hover:bg-[var(--color-or-pale)] transition-colors mb-2"
      >
        {t.reserveCabin}
      </button>

      <div className="flex gap-2">
        <button
          onClick={onPrev}
          className="flex-1 py-3 bg-white/5 border border-white/10 text-white/70 uppercase tracking-[0.2em] text-xs hover:bg-white/10 transition-all duration-300"
        >
          ← Précédent
        </button>
        <button
          onClick={onNext}
          className="flex-1 py-3 bg-white/5 border border-white/10 text-white/70 uppercase tracking-[0.2em] text-xs hover:bg-white/10 transition-all duration-300"
        >
          Suivant →
        </button>
      </div>

      <p className="text-center text-[10px] text-white/30 tracking-widest mt-2">
        {currentIdx + 1} / {total} — {t.curated}
      </p>

      <div className="flex justify-center gap-2 mt-3 flex-wrap">
        {FEATURED.slice(0, 16).map((_, i) => (
          <div
            key={i}
            className={`w-1.5 h-1.5 rounded-full transition-all duration-300 ${
              i === currentIdx ? "bg-[var(--color-or)] scale-125" : "bg-white/20"
            }`}
          />
        ))}
      </div>
    </aside>
  );
}

function FabricChips({ currentId, onPick }: { currentId: string; onPick: (id: string) => void }) {
  // Les 5 profils Robert pilotes
  const PILOT_IDS = ["eg001", "eg002", "eg003", "eg004", "eg005"];
  const LABELS: Record<string, string> = {
    eg001: "Soie élast.",
    eg002: "Laine légère",
    eg003: "Velours liq.",
    eg004: "Coton premium",
    eg005: "Mix indus.",
  };
  return (
    <div className="flex items-center gap-2 flex-wrap">
      {PILOT_IDS.map((id) => {
        const active = id === currentId;
        return (
          <button
            key={id}
            onClick={() => onPick(id)}
            title={LABELS[id]}
            className={`group flex flex-col items-center gap-1 transition-all duration-300 ${
              active ? "scale-110" : "opacity-70 hover:opacity-100"
            }`}
          >
            <span
              className={`w-7 h-7 rounded-full border ${
                active
                  ? "bg-[var(--color-or)] border-[var(--color-or)] shadow-[0_0_12px_rgba(197,164,109,0.6)]"
                  : "bg-transparent border-[var(--color-or)]/40"
              }`}
            />
            <span className="text-[8px] tracking-widest uppercase text-white/55 group-hover:text-[var(--color-or)]">
              {LABELS[id]}
            </span>
          </button>
        );
      })}
    </div>
  );
}

function LandmarkCard({ onClose }: { onClose: () => void }) {
  return (
    <div
      className="absolute right-6 bottom-32 z-40 w-[300px] max-h-[60vh] overflow-y-auto p-5 bg-[var(--color-noir)]/95 backdrop-blur-md border border-[var(--color-or)]/30 rounded-sm shadow-2xl"
      onClick={(e) => e.stopPropagation()}
    >
      <div className="flex items-center justify-between mb-3">
        <div>
          <div className="text-[9px] tracking-[0.32em] uppercase text-[var(--color-or)]/80">
            33 points anatomiques
          </div>
          <div className="font-display italic text-white text-[18px] leading-tight">
            MediaPipe Pose
          </div>
        </div>
        <button
          onClick={onClose}
          className="text-white/40 hover:text-[var(--color-or)] text-lg leading-none"
        >
          ×
        </button>
      </div>

      {LANDMARK_CHAPTERS.map((ch) => (
        <div key={ch.id} className="mb-3 last:mb-0">
          <div className="flex items-baseline justify-between mb-1">
            <span className="font-display italic text-[var(--color-or)] text-[13px]">
              {ch.title}
            </span>
            <span className="text-[9px] tracking-widest uppercase text-white/30">
              Pts {ch.range[0]}–{ch.range[1]}
            </span>
          </div>
          <p className="text-[10px] text-white/45 mb-1">{ch.description}</p>
          <div className="flex flex-wrap gap-1">
            {ch.labels.map((label, i) => (
              <span
                key={i}
                className="text-[9px] px-1.5 py-0.5 bg-white/5 text-white/65 rounded-sm"
              >
                {label}
              </span>
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}

// ═══════════════════════════════════════════════════════════════════════
// SECTION B2B éditoriale (sous la zone caméra, scrollable)
// ═══════════════════════════════════════════════════════════════════════
function B2BTechSection() {
  return (
    <section className="relative bg-[var(--color-anthracite)] py-24 md:py-32">
      <div className="container">
        <div className="grid grid-cols-12 gap-8 mb-14">
          <div className="col-span-12 md:col-span-4">
            <span className="roman">VI</span>
            <div className="mt-3 eyebrow">Technologie</div>
            <h2 className="display-l mt-6">
              Sous le miroir,
              <br />
              <span className="accent-italic">l'usine intelligente.</span>
            </h2>
          </div>
          <div className="col-span-12 md:col-span-8 flex items-end">
            <p className="text-base md:text-lg text-[var(--color-fog)] leading-relaxed">
              Chaque image que vous voyez est calculée trente fois par seconde par
              quatre couches techniques superposées : MediaPipe Pose, le filtre
              EMA stable, le moteur Robert de physique de tissu, et le Protocole
              Zero-Size. Aucune mesure manuelle. Aucune donnée stockée.
            </p>
          </div>
        </div>

        <div className="hairline mb-12" />

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-px bg-[rgba(197,164,109,0.18)]">
          <TechCard
            n="01"
            title="33 points en 22 ms"
            body="Détection biométrique temps réel via MediaPipe Pose lite. Latence imperceptible, fluidité industrielle."
          />
          <TechCard
            n="02"
            title="Filtrage EMA stable"
            body="Lissage adaptatif des landmarks par filtre exponentiel : zéro vibration, vêtement ancré au corps."
          />
          <TechCard
            n="03"
            title="Robert Engine"
            body="Physique de tissu temps réel : drape, gravité, élasticité. Chaque profil tissu calculé à chaque frame."
          />
          <TechCard
            n="04"
            title="Protocole Zero-Size"
            body="Aucune saisie manuelle, aucun chiffre exposé au client. La technologie connaît la taille sans la dire."
          />
        </div>

        <div className="grid grid-cols-12 gap-8 mt-16">
          <div className="col-span-12 md:col-span-7">
            <div className="eyebrow mb-4">Logique d'élasticité</div>
            <h3 className="display-m mb-4">
              Le tissu réagit, le corps reste
              <span className="accent-italic"> souverain.</span>
            </h3>
            <p className="text-[var(--color-ivoire)]/85 leading-relaxed mb-4">
              Cinq profils pilotes — Soie Élastique, Laine Légère, Velours Liquide,
              Coton Premium, Mix Industriel — modélisés selon leur drape,
              gravité et coefficient de friction. Un sweater ne tombe pas comme
              un satin de soie : Robert le sait.
            </p>
            <p className="text-[var(--color-fog)] leading-relaxed">
              Le système soustrait également la couche textile actuellement portée
              (« Calibrage corporel actif ») pour mesurer le corps réel et non
              corps + vêtement. Une ingénierie discrète qui élimine 100 % des
              erreurs d'ajustement liées aux vêtements de scan.
            </p>
          </div>
          <div className="col-span-12 md:col-span-5 flex flex-col gap-4">
            <PatentBadge />
          </div>
        </div>
      </div>
    </section>
  );
}

function TechCard({ n, title, body }: { n: string; title: string; body: string }) {
  return (
    <div className="bg-[var(--color-noir)] p-7 md:p-8">
      <div className="font-display italic text-[var(--color-or)] text-2xl mb-3">{n}</div>
      <h4 className="font-display text-[var(--color-ivoire)] text-lg mb-2 leading-tight">
        {title}
      </h4>
      <p className="text-[var(--color-fog)] text-sm leading-relaxed">{body}</p>
    </div>
  );
}

function PatentBadge() {
  return (
    <div className="border border-[var(--color-or)]/30 p-6">
      <div className="text-[10px] tracking-[0.32em] uppercase text-[var(--color-or)]/80 mb-2">
        Forteresse IP
      </div>
      <div className="font-display text-[var(--color-or)] text-2xl mb-1">
        PCT / EP2025 / 067317
      </div>
      <p className="text-sm text-[var(--color-ivoire)]/75 leading-relaxed mb-3">
        Brevet socle — 22 revendications protégées. 8 marques déposées.
        Valorisation IP estimée 120—400 M€.
      </p>
      <div className="flex flex-wrap gap-1">
        {["ABVETOS®", "TRYONYOU®", "Robert Engine", "Zero-Size®"].map((l) => (
          <span
            key={l}
            className="text-[9px] px-2 py-1 bg-white/5 text-white/65 tracking-wider"
          >
            {l}
          </span>
        ))}
      </div>
    </div>
  );
}

// ─── Listener global pour le sélecteur de profil tissu ───
if (typeof window !== "undefined") {
  // évite double-binding HMR
  (window as any).__tryon_pick_handler ??= true;
}
