/**
 * Maison Couture Nocturne — FabricSimulator
 *
 * Adapted from Faramarz336/TRYONME...modules/CAP/src/FabricSimulator.jsx
 * (Cloth Animation Pipeline). Original was a stub canvas; this version
 * implements an actual ribbon-fabric simulation in canvas2D using simple
 * verlet-style draping driven by the user's mouse/finger and a palette
 * matching the chosen fabric type.
 *
 * Visual language: gold thread + obsidian background, no rounded radii.
 */
import { useEffect, useRef, useState } from "react";

type FabricType = "soie" | "cachemire" | "denim" | "coton";

const FABRICS: Record<FabricType, { color: string; sheen: string; gravity: number; damping: number; tension: number }> = {
  soie:      { color: "#C9A84C", sheen: "#F0E6D2", gravity: 0.4, damping: 0.985, tension: 0.36 },
  cachemire: { color: "#A88456", sheen: "#D8BC6A", gravity: 0.6, damping: 0.978, tension: 0.30 },
  denim:     { color: "#2A3A52", sheen: "#5A7090", gravity: 0.9, damping: 0.965, tension: 0.46 },
  coton:     { color: "#F5EFE0", sheen: "#FFFFFF", gravity: 0.55, damping: 0.972, tension: 0.34 },
};

export default function FabricSimulator() {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [fabric, setFabric] = useState<FabricType>("soie");
  const fabricRef = useRef(fabric);
  fabricRef.current = fabric;

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    const COLS = 22;
    const ROWS = 18;
    let dpi = Math.min(window.devicePixelRatio, 2);
    let W = 0;
    let H = 0;

    type P = { x: number; y: number; px: number; py: number; pinned: boolean };
    type C = { a: number; b: number; rest: number };

    let points: P[] = [];
    let constraints: C[] = [];
    let mouse = { x: -9999, y: -9999, active: false };

    const resize = () => {
      const rect = canvas.getBoundingClientRect();
      dpi = Math.min(window.devicePixelRatio, 2);
      canvas.width = Math.floor(rect.width * dpi);
      canvas.height = Math.floor(rect.height * dpi);
      ctx.setTransform(dpi, 0, 0, dpi, 0, 0);
      W = rect.width;
      H = rect.height;
      // Build mesh
      const margin = 30;
      const usableW = W - margin * 2;
      const stepX = usableW / (COLS - 1);
      const stepY = (H * 0.55) / (ROWS - 1);
      points = [];
      for (let r = 0; r < ROWS; r++) {
        for (let c = 0; c < COLS; c++) {
          const x = margin + c * stepX;
          const y = 30 + r * stepY;
          points.push({ x, y, px: x, py: y, pinned: r === 0 });
        }
      }
      constraints = [];
      for (let r = 0; r < ROWS; r++) {
        for (let c = 0; c < COLS; c++) {
          const i = r * COLS + c;
          if (c < COLS - 1) constraints.push({ a: i, b: i + 1, rest: stepX });
          if (r < ROWS - 1) constraints.push({ a: i, b: i + COLS, rest: stepY });
        }
      }
    };

    const onMove = (e: PointerEvent) => {
      const rect = canvas.getBoundingClientRect();
      mouse.x = e.clientX - rect.left;
      mouse.y = e.clientY - rect.top;
      mouse.active = true;
    };
    const onLeave = () => { mouse.active = false; mouse.x = mouse.y = -9999; };

    canvas.addEventListener("pointermove", onMove);
    canvas.addEventListener("pointerleave", onLeave);
    window.addEventListener("resize", resize);
    resize();

    let raf = 0;
    const tick = () => {
      const cfg = FABRICS[fabricRef.current];

      // Verlet integration
      for (const p of points) {
        if (p.pinned) continue;
        const vx = (p.x - p.px) * cfg.damping;
        const vy = (p.y - p.py) * cfg.damping;
        p.px = p.x; p.py = p.y;
        p.x += vx;
        p.y += vy + cfg.gravity * 0.4;

        // Mouse drag
        if (mouse.active) {
          const dx = p.x - mouse.x;
          const dy = p.y - mouse.y;
          const d2 = dx * dx + dy * dy;
          if (d2 < 4500) {
            const f = (4500 - d2) / 4500;
            p.x += dx * 0.05 * f;
            p.y += dy * 0.05 * f;
          }
        }
      }

      // Constraint relaxation (2 passes)
      for (let pass = 0; pass < 2; pass++) {
        for (const c of constraints) {
          const a = points[c.a]; const b = points[c.b];
          const dx = b.x - a.x; const dy = b.y - a.y;
          const dist = Math.sqrt(dx * dx + dy * dy) || 0.0001;
          const diff = (dist - c.rest) / dist;
          const ox = dx * 0.5 * diff * cfg.tension;
          const oy = dy * 0.5 * diff * cfg.tension;
          if (!a.pinned) { a.x += ox; a.y += oy; }
          if (!b.pinned) { b.x -= ox; b.y -= oy; }
        }
      }

      // Render
      ctx.clearRect(0, 0, W, H);
      // Backdrop subtle gradient
      const g = ctx.createLinearGradient(0, 0, 0, H);
      g.addColorStop(0, "rgba(26,22,20,0.7)");
      g.addColorStop(1, "rgba(10,8,7,0.95)");
      ctx.fillStyle = g;
      ctx.fillRect(0, 0, W, H);

      // Cloth body — fill quads
      for (let r = 0; r < ROWS - 1; r++) {
        for (let c = 0; c < COLS - 1; c++) {
          const i = r * COLS + c;
          const a = points[i];
          const b = points[i + 1];
          const cP = points[i + COLS];
          const d = points[i + COLS + 1];
          const lit = ((a.y - cP.y) + (b.y - d.y)) * 0.5;
          const t = Math.max(0, Math.min(1, (lit + 30) / 60));
          ctx.fillStyle = mix(cfg.color, cfg.sheen, t * 0.45);
          ctx.beginPath();
          ctx.moveTo(a.x, a.y);
          ctx.lineTo(b.x, b.y);
          ctx.lineTo(d.x, d.y);
          ctx.lineTo(cP.x, cP.y);
          ctx.closePath();
          ctx.fill();
        }
      }

      // Cloth threads (gold hairlines)
      ctx.strokeStyle = "rgba(201,168,76,0.18)";
      ctx.lineWidth = 0.5;
      for (const co of constraints) {
        const a = points[co.a]; const b = points[co.b];
        ctx.beginPath();
        ctx.moveTo(a.x, a.y);
        ctx.lineTo(b.x, b.y);
        ctx.stroke();
      }

      raf = requestAnimationFrame(tick);
    };
    raf = requestAnimationFrame(tick);

    return () => {
      cancelAnimationFrame(raf);
      canvas.removeEventListener("pointermove", onMove);
      canvas.removeEventListener("pointerleave", onLeave);
      window.removeEventListener("resize", resize);
    };
  }, []);

  return (
    <div className="border border-[rgba(201,168,76,0.3)] bg-[rgba(10,8,7,0.6)]">
      <div className="flex items-center justify-between px-6 py-4 border-b border-[rgba(201,168,76,0.2)]">
        <div className="flex items-center gap-3">
          <span className="text-[var(--color-or)] font-display italic text-[20px]">
            Simulation textile
          </span>
          <span className="text-[10px] tracking-[0.24em] uppercase text-[var(--color-fog)]">
            CAP · Cloth Animation Pipeline
          </span>
        </div>
        <span className="text-[10px] tracking-[0.22em] uppercase text-[var(--color-or)]">
          Drapé physique · Live
        </span>
      </div>
      <div className="relative">
        <canvas ref={canvasRef} className="w-full h-[320px] block touch-none" />
        <div className="absolute bottom-3 left-4 text-[10px] tracking-[0.2em] uppercase text-[var(--color-fog)]">
          Glissez la souris pour caresser le drapé
        </div>
      </div>
      <div className="px-6 py-4 border-t border-[rgba(201,168,76,0.2)] flex flex-wrap gap-2">
        {(Object.keys(FABRICS) as FabricType[]).map((f) => (
          <button
            key={f}
            onClick={() => setFabric(f)}
            className={`px-4 py-2 text-[11px] tracking-[0.18em] uppercase border transition-all duration-500 ${
              fabric === f
                ? "border-[var(--color-or)] text-[var(--color-or)] bg-[rgba(201,168,76,0.08)]"
                : "border-[rgba(201,168,76,0.2)] text-[var(--color-ivoire)]/70 hover:border-[rgba(201,168,76,0.5)]"
            }`}
          >
            {f}
          </button>
        ))}
      </div>
    </div>
  );
}

function mix(a: string, b: string, t: number): string {
  const ra = parseInt(a.slice(1, 3), 16);
  const ga = parseInt(a.slice(3, 5), 16);
  const ba = parseInt(a.slice(5, 7), 16);
  const rb = parseInt(b.slice(1, 3), 16);
  const gb = parseInt(b.slice(3, 5), 16);
  const bb = parseInt(b.slice(5, 7), 16);
  const r = Math.round(ra + (rb - ra) * t);
  const g = Math.round(ga + (gb - ga) * t);
  const bl = Math.round(ba + (bb - ba) * t);
  return `rgb(${r},${g},${bl})`;
}
