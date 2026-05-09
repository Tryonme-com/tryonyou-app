/**
 * TRYONYOU — /tryon
 *
 * Live virtual try-on experience.
 *   • Webcam (1280×720, mirrored)
 *   • MediaPipe Pose loaded from CDN
 *   • Procedural SVG garment overlay anchored to MediaPipe landmarks
 *   • Right side panel with garment metadata + cycle button + lang selector
 *
 * Style: Maison Couture Nocturne — gold-on-graphite, editorial.
 */

import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { Link, useLocation } from "wouter";
import { FEATURED, type Garment, getGarmentBySku, FABRICS } from "@/lib/catalog";
import { LANG_PACKS, type Lang } from "@/lib/i18n";
import { loadOverlayImage } from "@/lib/garmentOverlays";
import { drawGarmentOverlay } from "@/lib/overlayRenderer";

type Phase = "permission" | "scanning" | "measuring" | "fitting";

declare global {
  interface Window {
    Pose?: any;
    __tryon_landmarks?: any;
  }
}

function loadScript(src: string): Promise<void> {
  return new Promise((resolve, reject) => {
    if (document.querySelector(`script[src="${src}"]`)) return resolve();
    const s = document.createElement("script");
    s.src = src;
    s.crossOrigin = "anonymous";
    s.onload = () => resolve();
    s.onerror = () => reject(new Error(`Failed to load ${src}`));
    document.head.appendChild(s);
  });
}

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

export default function TryOn() {
  const [location] = useLocation();
  const [lang, setLang] = useState<Lang>("fr");
  const [phase, setPhase] = useState<Phase>("permission");
  const [scanProgress, setScanProgress] = useState(0);
  const [permissionDenied, setPermissionDenied] = useState(false);
  const [statusMsg, setStatusMsg] = useState("");
  const [transitioning, setTransitioning] = useState(false);

  // Resolve initial sku from query string (?sku=EG-LAF-001)
  const initialIdx = useMemo(() => {
    const params = new URLSearchParams(window.location.search);
    const sku = params.get("sku");
    if (!sku) return 0;
    const idx = FEATURED.findIndex((g) => g.sku === sku || g.ref === sku);
    return idx >= 0 ? idx : 0;
  }, []);
  const [currentIdx, setCurrentIdx] = useState(initialIdx);

  // FitScore — synthesized client-side based on body+fabric
  const [fitScore, setFitScore] = useState(0);

  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const rafRef = useRef<number>(0);
  const poseRef = useRef<any>(null);
  const poseReadyRef = useRef(false);
  const lastSendRef = useRef(0);
  const overlaysRef = useRef<Map<string, HTMLImageElement>>(new Map());
  const anchorRef = useRef({
    cx: 0,
    sy: 0,
    hy: 0,
    sw: 0,
    angle: 0,
    detected: false,
    lastDetectedTime: 0,
  });
  const phaseRef = useRef<Phase>("permission");
  const idxRef = useRef(currentIdx);
  const measurementsRef = useRef({
    shoulderWidthPx: 0,
    torsoHeightPx: 0,
    hipWidthPx: 0,
    frameWidthPx: 1280,
    frameHeightPx: 720,
  });

  const t = LANG_PACKS[lang];
  const garment = FEATURED[currentIdx];
  const fabric = FABRICS[garment.fabricKey];

  // Sync refs
  useEffect(() => {
    idxRef.current = currentIdx;
  }, [currentIdx]);
  useEffect(() => {
    phaseRef.current = phase;
  }, [phase]);

  // Preload all overlays on mount (background)
  useEffect(() => {
    let cancelled = false;
    (async () => {
      for (const g of FEATURED) {
        if (cancelled) return;
        if (!overlaysRef.current.has(g.id)) {
          try {
            const img = await loadOverlayImage(g);
            overlaysRef.current.set(g.id, img);
          } catch (e) {
            console.warn("[TRYONYOU] overlay load failed:", g.id, e);
          }
        }
      }
    })();
    return () => {
      cancelled = true;
    };
  }, []);

  // Compute synthetic FitScore from body + fabric whenever measurements update
  const computeFitScore = useCallback((): number => {
    const m = measurementsRef.current;
    const a = anchorRef.current;
    if (!a.detected) return 88; // Demo mode baseline
    if (!fabric) return 92;

    // Body presence quality
    const bodyConfidence = Math.min(
      1,
      m.shoulderWidthPx > 80 ? 1 : m.shoulderWidthPx / 80,
    );

    // Drape × elasticity affinity — higher silk-like fabric → higher score
    const drapeBonus = fabric.drapeCoefficient * 6;
    const elasticBonus = (fabric.elasticityPct / 25) * 4;
    const recoveryBonus = (fabric.recoveryPct / 100) * 3;
    const score = 86 + drapeBonus + elasticBonus + recoveryBonus;
    return Math.round(Math.max(78, Math.min(99, score * bodyConfidence)));
  }, [fabric]);

  // Render loop
  const renderFrame = useCallback(() => {
    const canvas = canvasRef.current;
    const video = videoRef.current;
    if (!canvas || !video || video.readyState < 2) {
      rafRef.current = requestAnimationFrame(renderFrame);
      return;
    }
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    const W = video.videoWidth || 1280;
    const H = video.videoHeight || 720;
    if (canvas.width !== W || canvas.height !== H) {
      canvas.width = W;
      canvas.height = H;
    }

    ctx.clearRect(0, 0, W, H);

    const a = anchorRef.current;
    const now = Date.now();
    const hasBody = a.detected && now - a.lastDetectedTime < 2000;
    const portrait = H > W;

    let cx: number,
      sy: number,
      hy: number,
      sw: number,
      angle: number;
    if (hasBody) {
      cx = a.cx;
      sy = a.sy;
      hy = a.hy;
      sw = a.sw;
      angle = a.angle;
    } else {
      cx = W / 2;
      sy = portrait ? H * 0.38 : H * 0.3;
      hy = portrait ? H * 0.68 : H * 0.65;
      sw = portrait ? W * 0.35 : W * 0.22;
      angle = 0;
    }

    // Halo behind garment
    const haloR = hasBody ? sw * 2.5 : W * 0.35;
    const halo = ctx.createRadialGradient(cx, sy + (hy - sy) * 0.4, sw * 0.2, cx, sy + (hy - sy) * 0.4, haloR);
    halo.addColorStop(0, "rgba(201, 168, 76, 0.08)");
    halo.addColorStop(0.5, "rgba(201, 168, 76, 0.03)");
    halo.addColorStop(1, "rgba(201, 168, 76, 0)");
    ctx.fillStyle = halo;
    ctx.fillRect(0, 0, W, H);

    // Garment overlay
    const g = FEATURED[idxRef.current];
    const img = overlaysRef.current.get(g.id);
    if (phaseRef.current === "fitting" && img) {
      const score = computeFitScore();
      const baseAnchor = hasBody
        ? { cx, shoulderY: sy, hipY: hy, shoulderW: sw, angle, hasBody }
        : {
            cx: W / 2,
            shoulderY: (portrait ? H * 0.38 : H * 0.28) + Math.sin(now * 0.0015) * 6,
            hipY: (portrait ? H * 0.68 : H * 0.62) + Math.sin(now * 0.0015) * 6,
            shoulderW: portrait ? W * 0.35 : W * 0.24,
            angle: 0,
            hasBody: false,
          };
      try {
        drawGarmentOverlay(ctx, img, baseAnchor, g, score, W, H);
      } catch (e) {
        console.warn("[TRYONYOU] overlay error:", e);
      }
      // Periodically refresh fitScore state for the side panel
      if (Math.floor(now / 500) % 2 === 0) {
        setFitScore((prev) => (Math.abs(prev - score) > 1 ? score : prev));
      }
      if (!hasBody) {
        ctx.save();
        ctx.fillStyle = "rgba(201, 168, 76, 0.7)";
        ctx.font = "12px sans-serif";
        ctx.textAlign = "center";
        ctx.fillText(
          "Mode Smart — placez-vous face à la caméra pour l'ancrage AR",
          W / 2,
          H - 25,
        );
        ctx.restore();
      }
    } else if (phaseRef.current === "measuring") {
      ctx.save();
      ctx.globalAlpha = 0.7;
      ctx.fillStyle = "#C9A84C";
      ctx.font = "12px monospace";
      ctx.textAlign = "center";
      ctx.fillText(
        hasBody ? "CORPS DÉTECTÉ — extraction des mesures…" : "RECHERCHE DU CORPS…",
        W / 2,
        H - 40,
      );
      ctx.restore();
    }

    // Skeleton (when body detected)
    if (hasBody && window.__tryon_landmarks) {
      const lm = window.__tryon_landmarks;
      const limbs: [number, number][] = [
        [11, 13],
        [13, 15],
        [12, 14],
        [14, 16],
        [23, 25],
        [25, 27],
        [24, 26],
        [26, 28],
      ];
      ctx.strokeStyle = "rgba(0, 210, 255, 0.35)";
      ctx.lineWidth = 2;
      for (const [a2, b] of limbs) {
        const A = lm[a2];
        const B = lm[b];
        if (A && B && A.visibility > 0.25 && B.visibility > 0.25) {
          ctx.beginPath();
          ctx.moveTo(A.x * W, A.y * H);
          ctx.lineTo(B.x * W, B.y * H);
          ctx.stroke();
        }
      }
      // Torso quadrilateral in gold
      ctx.strokeStyle = "rgba(201, 168, 76, 0.5)";
      ctx.lineWidth = 2.5;
      const torso: [number, number][] = [
        [11, 12],
        [11, 23],
        [12, 24],
        [23, 24],
      ];
      for (const [a2, b] of torso) {
        const A = lm[a2];
        const B = lm[b];
        if (A && B && A.visibility > 0.25 && B.visibility > 0.25) {
          ctx.beginPath();
          ctx.moveTo(A.x * W, A.y * H);
          ctx.lineTo(B.x * W, B.y * H);
          ctx.stroke();
        }
      }
    }

    // Scanline gold
    const sy2 = ((now % 3000) / 3000) * H;
    const grad = ctx.createLinearGradient(0, sy2 - 2, 0, sy2 + 2);
    grad.addColorStop(0, "rgba(201, 168, 76, 0)");
    grad.addColorStop(0.5, "rgba(201, 168, 76, 0.12)");
    grad.addColorStop(1, "rgba(201, 168, 76, 0)");
    ctx.fillStyle = grad;
    ctx.fillRect(0, sy2 - 15, W, 30);

    // Send frame to MediaPipe
    if (poseReadyRef.current && poseRef.current && video.readyState >= 2) {
      const interval = phaseRef.current === "fitting" || phaseRef.current === "measuring" ? 50 : 150;
      if (now - lastSendRef.current > interval) {
        lastSendRef.current = now;
        try {
          poseRef.current.send({ image: video });
        } catch (e) {
          console.warn("[TRYONYOU] pose.send error:", e);
        }
      }
    }

    rafRef.current = requestAnimationFrame(renderFrame);
  }, [computeFitScore]);

  // MediaPipe init
  const initPose = useCallback(async (): Promise<boolean> => {
    try {
      await loadScript("https://cdn.jsdelivr.net/npm/@mediapipe/pose@0.5.1675469404/pose.js");
      const Pose = window.Pose;
      if (!Pose) throw new Error("Pose class missing");
      const pose = new Pose({
        locateFile: (file: string) =>
          `https://cdn.jsdelivr.net/npm/@mediapipe/pose@0.5.1675469404/${file}`,
      });
      pose.setOptions({
        modelComplexity: 1,
        smoothLandmarks: true,
        enableSegmentation: false,
        minDetectionConfidence: 0.5,
        minTrackingConfidence: 0.5,
      });
      pose.onResults((results: any) => {
        if (!results.poseLandmarks || results.poseLandmarks.length < 25) return;
        const L = results.poseLandmarks;
        const lShoulder = L[11];
        const rShoulder = L[12];
        const lHip = L[23];
        const rHip = L[24];
        if (
          !lShoulder ||
          !rShoulder ||
          !lHip ||
          !rHip ||
          lShoulder.visibility < 0.3 ||
          rShoulder.visibility < 0.3
        ) return;
        const c = canvasRef.current;
        const W = c?.width || 1280;
        const H = c?.height || 720;
        const lx = lShoulder.x * W;
        const rx = rShoulder.x * W;
        const cx = (lx + rx) / 2;
        const sy = ((lShoulder.y + rShoulder.y) / 2) * H;
        const hy = ((lHip.y + rHip.y) / 2) * H;
        const sw = Math.abs(rx - lx);
        const angle = Math.atan2((rShoulder.y - lShoulder.y) * H, rx - lx);
        const k = 0.35;
        const prev = anchorRef.current;
        const fresh = prev.detected && Date.now() - prev.lastDetectedTime < 1000;
        anchorRef.current = {
          cx: fresh ? prev.cx + (cx - prev.cx) * k : cx,
          sy: fresh ? prev.sy + (sy - prev.sy) * k : sy,
          hy: fresh ? prev.hy + (hy - prev.hy) * k : hy,
          sw: fresh ? prev.sw + (sw - prev.sw) * k : sw,
          angle: fresh ? prev.angle + (angle - prev.angle) * k : angle,
          detected: true,
          lastDetectedTime: Date.now(),
        };
        window.__tryon_landmarks = L;

        const lhx = lHip.x * W;
        const rhx = rHip.x * W;
        const hipW = Math.abs(rhx - lhx);
        measurementsRef.current = {
          shoulderWidthPx: sw,
          torsoHeightPx: Math.max(0, hy - sy),
          hipWidthPx: hipW > 0 ? hipW : sw * 0.9,
          frameWidthPx: W,
          frameHeightPx: H,
        };
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

  const startCamera = useCallback(async () => {
    setPhase("scanning");
    setScanProgress(0);
    setPermissionDenied(false);
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { facingMode: "user", width: { ideal: 1280 }, height: { ideal: 720 } },
        audio: false,
      });
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
    rafRef.current = requestAnimationFrame(renderFrame);

    const poseInit = initPose();
    let progress = 0;
    let resolved = false;
    const id = setInterval(async () => {
      if (progress < 85) {
        progress += Math.random() * 5 + 3;
      } else if (!resolved) {
        resolved = true;
        const timeout = new Promise<boolean>((r) => setTimeout(() => r(false), 8000));
        await Promise.race([poseInit, timeout]);
        progress = 100;
      }
      if (progress >= 100) {
        progress = 100;
        clearInterval(id);
        setPhase("measuring");
        setStatusMsg(t.measuring);
      }
      setScanProgress(Math.min(100, progress));
    }, 200);
  }, [initPose, renderFrame, t]);

  // Measuring → Fitting transition
  useEffect(() => {
    if (phase !== "measuring") return;
    setStatusMsg(t.measuring);
    const start = Date.now();
    const id = setInterval(() => {
      const a = anchorRef.current;
      const detected = a.detected && Date.now() - a.lastDetectedTime < 2000;
      if (detected && measurementsRef.current.shoulderWidthPx > 50) {
        setStatusMsg(t.bodyDetected);
        setTimeout(() => {
          setPhase("fitting");
          setStatusMsg("");
        }, 1200);
        clearInterval(id);
      } else if (Date.now() - start > 12000) {
        // Demo fallback: enter fitting anyway
        setStatusMsg(t.bodyDetected);
        setTimeout(() => {
          setPhase("fitting");
          setStatusMsg("");
        }, 800);
        clearInterval(id);
      }
    }, 400);
    return () => clearInterval(id);
  }, [phase, t]);

  const cycleGarment = useCallback(() => {
    setTransitioning(true);
    setTimeout(() => {
      setCurrentIdx((i) => (i + 1) % FEATURED.length);
      setTransitioning(false);
    }, 500);
  }, []);

  // Cleanup
  useEffect(() => {
    return () => {
      if (rafRef.current) cancelAnimationFrame(rafRef.current);
      if (streamRef.current) {
        streamRef.current.getTracks().forEach((tk) => tk.stop());
      }
    };
  }, []);

  const isPerfectFit = fitScore >= 95;

  return (
    <div className="relative w-full h-screen bg-[var(--color-noir)] overflow-hidden">
      {/* Video & Canvas */}
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
        style={{ transform: "scaleX(-1)", objectFit: "cover" }}
      />

      {/* Top bar */}
      <header className="absolute top-0 left-0 right-0 z-30 flex items-center justify-between px-6 py-4 bg-gradient-to-b from-black/70 to-transparent">
        <Link href="/" className="text-[10px] tracking-[0.32em] uppercase text-white/60 hover:text-[var(--color-or)] transition-colors">
          ← {t.back}
        </Link>
        <div className="font-display text-[var(--color-or)] text-[18px] tracking-[0.32em]">
          {t.brand}
        </div>
        <LangSelector lang={lang} setLang={setLang} />
      </header>

      {/* Permission overlay */}
      {phase === "permission" && (
        <div className="absolute inset-0 z-40 flex items-center justify-center bg-[var(--color-noir)]/90 backdrop-blur-md">
          <div className="max-w-md text-center px-8">
            <div className="font-display text-[var(--color-or)] italic text-[42px] leading-tight mb-4">
              {t.permissionTitle}
            </div>
            <p className="text-[15px] text-white/70 leading-[1.7] mb-8">{t.permissionLede}</p>
            {permissionDenied && (
              <p className="text-[12px] text-red-400/80 mb-4">{t.permissionDenied}</p>
            )}
            <button onClick={startCamera} className="btn-or inline-flex">
              {t.permissionCTA}
              <span aria-hidden>→</span>
            </button>
          </div>
        </div>
      )}

      {/* Scanning overlay */}
      {phase === "scanning" && (
        <div className="absolute inset-0 z-30 flex items-center justify-center bg-[var(--color-noir)]/40 backdrop-blur-sm pointer-events-none">
          <div className="text-center">
            <div className="text-[10px] tracking-[0.32em] uppercase text-[var(--color-or)] mb-4">
              {t.scanning}
            </div>
            <div className="w-64 h-px bg-white/10 mx-auto overflow-hidden">
              <div
                className="h-full bg-[var(--color-or)] transition-all duration-300"
                style={{ width: `${scanProgress}%` }}
              />
            </div>
            <div className="font-display text-[var(--color-or)] text-[28px] mt-3">
              {Math.round(scanProgress)}%
            </div>
          </div>
        </div>
      )}

      {/* Measuring status pill */}
      {phase === "measuring" && (
        <div className="absolute bottom-24 left-1/2 -translate-x-1/2 z-30 px-5 py-3 rounded-sm bg-[var(--color-noir)]/80 backdrop-blur-sm border border-[var(--color-or)]/30">
          <div className="flex items-center gap-3 text-[12px] text-[var(--color-or)] tracking-wide">
            <span className="w-2 h-2 rounded-full bg-[var(--color-or)] animate-pulse" />
            {statusMsg}
          </div>
        </div>
      )}

      {/* Side panel */}
      {phase === "fitting" && (
        <aside
          className={`absolute right-0 top-0 bottom-0 w-full sm:w-[380px] z-20 bg-[var(--color-noir)]/85 backdrop-blur-md border-l border-white/5 flex flex-col p-6 pt-20 transition-opacity duration-500 ${
            transitioning ? "opacity-0" : "opacity-100"
          }`}
        >
          <div className="mb-2 text-[10px] tracking-[0.32em] uppercase text-[var(--color-or)]/70">
            {t.collection}
          </div>
          <h2 className="font-display text-white text-[28px] leading-tight mb-1">{garment.name}</h2>
          <div className="text-[11px] tracking-widest uppercase text-white/40 mb-5">
            {garment.designer}
          </div>

          {/* Fit panel */}
          {isPerfectFit ? (
            <div className="mb-5 p-4 rounded-sm bg-[var(--color-or)]/10 border border-[var(--color-or)]/30">
              <div className="flex items-center gap-2 mb-2">
                <div className="w-2.5 h-2.5 rounded-full bg-[var(--color-or)] animate-pulse" />
                <span className="font-display text-[18px] tracking-wide text-[var(--color-or)]">
                  {t.perfectFit}
                </span>
              </div>
              <div className="w-full h-1 bg-white/10 rounded-full overflow-hidden">
                <div
                  className="h-full rounded-full bg-[var(--color-or)] transition-all duration-700"
                  style={{ width: "100%" }}
                />
              </div>
              <p className="text-[10px] mt-2 italic text-[var(--color-or)]/60">{t.validatedBy}</p>
            </div>
          ) : (
            <div className="mb-5 p-4 rounded-sm bg-white/5 border border-white/10">
              <div className="flex items-center gap-2 mb-2">
                <div className="w-2 h-2 rounded-full bg-amber-400 animate-pulse" />
                <span className="text-[10px] text-white/50 tracking-widest uppercase">
                  {t.recalculating}
                </span>
              </div>
              <div className="w-full h-1 bg-white/10 rounded-full overflow-hidden">
                <div
                  className="h-full rounded-full bg-amber-400/60 transition-all duration-1000"
                  style={{ width: `${Math.min(95, fitScore)}%` }}
                />
              </div>
              <p className="text-[10px] mt-2 italic text-white/30">
                {fitScore || "—"}%
              </p>
            </div>
          )}

          {/* Fabric / drape grid */}
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

          <button
            onClick={() => alert("Réservation envoyée à votre boutique de référence.")}
            className="w-full py-4 bg-[var(--color-or)] text-[var(--color-noir)] uppercase tracking-[0.2em] text-sm font-bold hover:bg-[#dbb866] transition-all duration-300 mb-2"
          >
            {t.reserveCabin}
          </button>
          <button
            onClick={cycleGarment}
            className="w-full py-3 bg-white/5 border border-white/10 text-white/70 uppercase tracking-[0.2em] text-xs hover:bg-white/10 transition-all duration-300 mb-2"
          >
            {t.showMore} — {currentIdx + 1}/{FEATURED.length}
          </button>
          <p className="text-center text-[10px] text-white/30 tracking-widest">{t.curated}</p>

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
      )}

      {/* Footer */}
      <footer className="absolute bottom-0 left-0 right-0 z-30 border-t border-white/5 px-6 py-2 flex items-center justify-between bg-[var(--color-noir)]/70 backdrop-blur-sm">
        <p className="text-[9px] text-white/15 tracking-[0.3em] uppercase">{t.patent}</p>
        <p className="text-[9px] text-white/15 tracking-[0.3em] uppercase">© 2026 TRYONYOU</p>
      </footer>
    </div>
  );
}
