/**
 * TRYONYOU — /tryon
 *
 * Cinematic four-phase try-on experience:
 *   1) CAMERA  — webcam opens, user sees themselves clean, no overlay.
 *   2) WIREFRAME — body silhouette becomes a low-poly gold mesh (no measurements ever displayed).
 *   3) SWIRL — golden particle storm wraps around the avatar.
 *   4) REVEAL — the swirl dissipates, the garment overlay materializes on the real body.
 *
 * No numerical body data is ever surfaced to the UI; the only score the user sees is the
 * symbolic "Ajustement : Parfait" label once the garment has been projected.
 */

import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { Link } from "wouter";
import { FEATURED, FABRICS } from "@/lib/catalog";
import { LANG_PACKS, type Lang } from "@/lib/i18n";
import { loadOverlayImage } from "@/lib/garmentOverlays";
import { drawGarmentOverlay } from "@/lib/overlayRenderer";
import {
  GoldenSwirl,
  bodyBox,
  drawTriangulatedAvatar,
  easeInOutCubic,
  easeOutCubic,
  isPoseUsable,
} from "@/lib/cinematic";

// Phases of the cinematic pipeline.
//   - permission : pre-camera consent screen
//   - camera     : webcam visible, MediaPipe warming up
//   - wireframe  : gold low-poly avatar drawn over body
//   - swirl      : particles converge & envelop body
//   - reveal     : garment overlay materializes (final state)
type Phase = "permission" | "camera" | "wireframe" | "swirl" | "reveal";

// Phase durations (ms)
const T_CAMERA_MIN = 1400;     // give the user a moment to see themselves
const T_WIREFRAME = 2400;
const T_SWIRL = 2800;
const T_REVEAL_FADE_IN = 900;  // garment fades in over this period

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
  const [lang, setLang] = useState<Lang>("fr");
  const [phase, setPhase] = useState<Phase>("permission");
  const [permissionDenied, setPermissionDenied] = useState(false);
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

  // Refs for the render loop
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const rafRef = useRef<number>(0);
  const poseRef = useRef<any>(null);
  const poseReadyRef = useRef(false);
  const lastSendRef = useRef(0);
  const overlaysRef = useRef<Map<string, HTMLImageElement>>(new Map());

  // Smoothed anchor (used by the garment overlay during the REVEAL phase).
  const anchorRef = useRef({
    cx: 0,
    sy: 0,
    hy: 0,
    sw: 0,
    angle: 0,
    detected: false,
    lastDetectedTime: 0,
  });

  // Phase machine references
  const phaseRef = useRef<Phase>("permission");
  const idxRef = useRef(currentIdx);
  const cameraStartRef = useRef(0);
  const wireframeStartRef = useRef(0);
  const swirlStartRef = useRef(0);
  const revealStartRef = useRef(0);
  const swirlRef = useRef<GoldenSwirl>(new GoldenSwirl(280));
  // First time we have a usable pose since the camera started.
  const firstPoseAtRef = useRef(0);

  const t = LANG_PACKS[lang];
  const garment = FEATURED[currentIdx];
  const fabric = FABRICS[garment.fabricKey];

  useEffect(() => {
    idxRef.current = currentIdx;
  }, [currentIdx]);
  useEffect(() => {
    phaseRef.current = phase;
  }, [phase]);

  // Preload garment overlays in the background.
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

  // ------------------------------------------------------------------
  // RENDER LOOP
  // ------------------------------------------------------------------
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
    const now = performance.now();
    const wallNow = Date.now();
    const hasBody = a.detected && wallNow - a.lastDetectedTime < 1500;
    const lm = window.__tryon_landmarks;
    const usablePose = isPoseUsable(lm);

    if (usablePose && firstPoseAtRef.current === 0) {
      firstPoseAtRef.current = now;
    }

    // -------- Phase transitions (driven by elapsed time + pose availability) --------
    if (phaseRef.current === "camera") {
      const sinceStart = now - cameraStartRef.current;
      if (sinceStart > T_CAMERA_MIN && usablePose) {
        wireframeStartRef.current = now;
        setPhase("wireframe");
      }
    } else if (phaseRef.current === "wireframe") {
      const sinceStart = now - wireframeStartRef.current;
      if (sinceStart > T_WIREFRAME) {
        swirlStartRef.current = now;
        swirlRef.current.start(now);
        setPhase("swirl");
      }
    } else if (phaseRef.current === "swirl") {
      const sinceStart = now - swirlStartRef.current;
      if (sinceStart > T_SWIRL) {
        revealStartRef.current = now;
        setPhase("reveal");
      }
    }

    // -------- Visual layers per phase --------
    const portrait = H > W;
    const fallbackBox = {
      cx: W / 2,
      cy: H * 0.5,
      width: portrait ? W * 0.55 : W * 0.32,
      height: H * 0.65,
    };
    const live = lm ? bodyBox(lm, W, H) : null;
    const box = live ?? fallbackBox;

    // Soft halo behind the body (always present from wireframe onward — adds magic).
    if (phaseRef.current !== "camera" && phaseRef.current !== "permission") {
      const haloR = Math.max(box.width, box.height) * 0.7;
      const halo = ctx.createRadialGradient(box.cx, box.cy, 0, box.cx, box.cy, haloR);
      halo.addColorStop(0, "rgba(201, 168, 76, 0.10)");
      halo.addColorStop(0.6, "rgba(201, 168, 76, 0.04)");
      halo.addColorStop(1, "rgba(201, 168, 76, 0)");
      ctx.fillStyle = halo;
      ctx.beginPath();
      ctx.arc(box.cx, box.cy, haloR, 0, Math.PI * 2);
      ctx.fill();
    }

    if (phaseRef.current === "wireframe") {
      const since = now - wireframeStartRef.current;
      const fadeIn = Math.min(1, since / 600);
      const pulse = 0.5 + 0.5 * Math.sin(now * 0.004);
      if (usablePose && lm) {
        drawTriangulatedAvatar(ctx, lm, W, H, easeOutCubic(fadeIn), pulse);
      }
    } else if (phaseRef.current === "swirl") {
      const sinceStart = now - swirlStartRef.current;
      const swirlT = Math.min(1, sinceStart / T_SWIRL);
      // Wireframe fades out during the first 60% of the swirl.
      const wireFade = Math.max(0, 1 - swirlT / 0.6);
      if (usablePose && lm && wireFade > 0.05) {
        drawTriangulatedAvatar(ctx, lm, W, H, wireFade, 1);
      }
      // Particles
      swirlRef.current.update(ctx, box, now, T_SWIRL);
    } else if (phaseRef.current === "reveal") {
      const sinceReveal = now - revealStartRef.current;
      const revealT = Math.min(1, sinceReveal / T_REVEAL_FADE_IN);
      const eased = easeInOutCubic(revealT);

      // Brief residual sparkle as the swirl exhales (first 300 ms of reveal).
      if (sinceReveal < 700 && usablePose) {
        const residualAlpha = 1 - Math.min(1, sinceReveal / 700);
        ctx.save();
        ctx.globalAlpha = residualAlpha * 0.6;
        swirlRef.current.update(ctx, box, now, T_SWIRL * 0.5);
        ctx.restore();
      }

      // Garment overlay (fades in)
      const g = FEATURED[idxRef.current];
      const img = overlaysRef.current.get(g.id);
      if (img) {
        const baseAnchor = hasBody
          ? {
              cx: a.cx,
              shoulderY: a.sy,
              hipY: a.hy,
              shoulderW: a.sw,
              angle: a.angle,
              hasBody: true,
            }
          : {
              cx: W / 2,
              shoulderY: (portrait ? H * 0.38 : H * 0.28) +
                Math.sin(now * 0.0015) * 6,
              hipY: (portrait ? H * 0.68 : H * 0.62) +
                Math.sin(now * 0.0015) * 6,
              shoulderW: portrait ? W * 0.35 : W * 0.24,
              angle: 0,
              hasBody: false,
            };
        ctx.save();
        ctx.globalAlpha = eased;
        try {
          // We pass a synthetic fitScore≥95 so the renderer applies the gold specular highlight.
          drawGarmentOverlay(ctx, img, baseAnchor, g, 96, W, H);
        } catch (e) {
          console.warn("[TRYONYOU] overlay error:", e);
        }
        ctx.restore();
      }
    }

    // Send frame to MediaPipe (continuously once initialized).
    if (poseReadyRef.current && poseRef.current && video.readyState >= 2) {
      const interval =
        phaseRef.current === "camera" || phaseRef.current === "wireframe" ? 80 : 130;
      if (wallNow - lastSendRef.current > interval) {
        lastSendRef.current = wallNow;
        try {
          poseRef.current.send({ image: video });
        } catch (e) {
          console.warn("[TRYONYOU] pose.send error:", e);
        }
      }
    }

    rafRef.current = requestAnimationFrame(renderFrame);
  }, []);

  // ------------------------------------------------------------------
  // MediaPipe init
  // ------------------------------------------------------------------
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
          !lShoulder || !rShoulder || !lHip || !rHip ||
          lShoulder.visibility < 0.3 || rShoulder.visibility < 0.3
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

  // ------------------------------------------------------------------
  // Camera startup
  // ------------------------------------------------------------------
  const startCamera = useCallback(async () => {
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
    cameraStartRef.current = performance.now();
    firstPoseAtRef.current = 0;
    setPhase("camera");
    rafRef.current = requestAnimationFrame(renderFrame);
    initPose();

    // Safety net: if MediaPipe never produces a usable pose within 7 s, advance anyway
    // so the user still sees the cinematic flow with a virtual centered avatar.
    setTimeout(() => {
      if (phaseRef.current === "camera") {
        wireframeStartRef.current = performance.now();
        setPhase("wireframe");
      }
    }, 7000);
  }, [initPose, renderFrame]);

  const cycleGarment = useCallback(() => {
    setTransitioning(true);
    setTimeout(() => {
      setCurrentIdx((i) => (i + 1) % FEATURED.length);
      setTransitioning(false);
    }, 500);
  }, []);

  // Replay the cinematic sequence with the current garment.
  const replayCinematic = useCallback(() => {
    if (phaseRef.current === "permission") return;
    cameraStartRef.current = performance.now();
    setPhase("camera");
    setTimeout(() => {
      if (phaseRef.current === "camera") {
        wireframeStartRef.current = performance.now();
        setPhase("wireframe");
      }
    }, T_CAMERA_MIN + 200);
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

  // Active-phase HUD label (top center, very subtle).
  const phaseLabel: string | null =
    phase === "camera"
      ? t.phaseCalibration
      : phase === "wireframe"
      ? t.phaseAnalysis
      : phase === "swirl"
      ? t.phaseMaterializing
      : phase === "reveal"
      ? t.phaseReady
      : null;

  return (
    <div className="relative w-full h-screen bg-[var(--color-noir)] overflow-hidden">
      {/* Video & canvas */}
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

      {/* Phase HUD (centered, very subtle) */}
      {phaseLabel && phase !== "permission" && (
        <div
          key={phase}
          className="absolute left-1/2 top-24 -translate-x-1/2 z-30 pointer-events-none"
        >
          <div className="flex items-center gap-3 px-4 py-2 rounded-sm bg-[var(--color-noir)]/55 backdrop-blur-sm border border-[var(--color-or)]/25 transition-all duration-700">
            <span className="w-1.5 h-1.5 rounded-full bg-[var(--color-or)] animate-pulse" />
            <span className="text-[10px] tracking-[0.32em] uppercase text-[var(--color-or)]">
              {phaseLabel}
            </span>
          </div>
        </div>
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
              {t.permissionCTA}
              <span aria-hidden>→</span>
            </button>
          </div>
        </div>
      )}

      {/* Side panel — only during reveal phase, animated in */}
      {phase === "reveal" && (
        <aside
          className={`absolute right-0 top-0 bottom-0 w-full sm:w-[380px] z-20 bg-[var(--color-noir)]/85 backdrop-blur-md border-l border-white/5 flex flex-col p-6 pt-20 transition-all duration-700 ${
            transitioning ? "opacity-0 translate-x-3" : "opacity-100 translate-x-0"
          }`}
          style={{
            animation: "tryonRevealIn 700ms cubic-bezier(0.16,1,0.3,1) both",
          }}
        >
          <div className="mb-2 text-[10px] tracking-[0.32em] uppercase text-[var(--color-or)]/70">
            {t.collection}
          </div>
          <h2 className="font-display text-white text-[28px] leading-tight mb-1">
            {garment.name}
          </h2>
          <div className="text-[11px] tracking-widest uppercase text-white/40 mb-5">
            {garment.designer}
          </div>

          {/* Symbolic fit indicator (no numerical score visible to the user) */}
          <div className="mb-5 p-4 rounded-sm bg-[var(--color-or)]/10 border border-[var(--color-or)]/30">
            <div className="flex items-center gap-2 mb-2">
              <div className="w-2.5 h-2.5 rounded-full bg-[var(--color-or)] animate-pulse" />
              <span className="font-display text-[18px] tracking-wide text-[var(--color-or)]">
                {t.perfectFit}
              </span>
            </div>
            <div className="w-full h-[2px] bg-white/10 overflow-hidden">
              <div
                className="h-full bg-[var(--color-or)] transition-all duration-1000"
                style={{ width: "100%" }}
              />
            </div>
            <p className="text-[10px] mt-2 italic text-[var(--color-or)]/60">
              {t.validatedBy}
            </p>
          </div>

          {/* Fabric / drape grid */}
          <div className="grid grid-cols-2 gap-3 mb-5">
            <div className="bg-white/5 p-3 rounded-sm">
              <p className="text-[9px] text-white/30 tracking-widest uppercase mb-1">
                {t.fabric}
              </p>
              <p className="text-[12px] text-white/70 leading-tight">{garment.fabricName}</p>
            </div>
            <div className="bg-white/5 p-3 rounded-sm">
              <p className="text-[9px] text-white/30 tracking-widest uppercase mb-1">
                {t.drape}
              </p>
              <p className="text-[12px] text-white/70">
                {fabric ? Math.round(fabric.drapeCoefficient * 100) : "—"}/100
              </p>
            </div>
          </div>

          <div className="flex items-baseline justify-between mb-5">
            <span className="text-[10px] tracking-widest uppercase text-white/40">
              {garment.ref}
            </span>
            <span className="font-display text-[var(--color-or)] text-[22px]">
              € {garment.price}
            </span>
          </div>

          <div className="flex-1" />

          <button
            onClick={() => alert("Réservation envoyée à votre boutique de référence.")}
            className="w-full py-4 bg-[var(--color-or)] text-[var(--color-noir)] uppercase tracking-[0.2em] text-sm font-bold hover:bg-[#dbb866] transition-all duration-300 mb-2"
          >
            {t.reserveCabin}
          </button>
          <button
            onClick={() => {
              cycleGarment();
              setTimeout(replayCinematic, 550);
            }}
            className="w-full py-3 bg-white/5 border border-white/10 text-white/70 uppercase tracking-[0.2em] text-xs hover:bg-white/10 transition-all duration-300 mb-2"
          >
            {t.showMore} — {currentIdx + 1}/{FEATURED.length}
          </button>
          <p className="text-center text-[10px] text-white/30 tracking-widest">
            {t.curated}
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
      )}

      {/* Footer */}
      <footer className="absolute bottom-0 left-0 right-0 z-30 border-t border-white/5 px-6 py-2 flex items-center justify-between bg-[var(--color-noir)]/70 backdrop-blur-sm">
        <p className="text-[9px] text-white/15 tracking-[0.3em] uppercase">{t.patent}</p>
        <p className="text-[9px] text-white/15 tracking-[0.3em] uppercase">© 2026 TRYONYOU</p>
      </footer>

      {/* Phase keyframes */}
      <style>{`
        @keyframes tryonRevealIn {
          0% { opacity: 0; transform: translateX(20px); }
          100% { opacity: 1; transform: translateX(0); }
        }
      `}</style>
    </div>
  );
}
