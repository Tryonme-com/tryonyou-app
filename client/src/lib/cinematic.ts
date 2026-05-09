/**
 * TRYONYOU — Cinematic helpers for /tryon
 *
 * Two visual primitives the renderer composes per phase:
 *   1) drawTriangulatedAvatar() — low-poly gold mesh derived from MediaPipe Pose landmarks.
 *   2) GoldenSwirl — particle system (sparkles spiraling around the body center) that gradually
 *      envelops the silhouette, then dissipates so the garment can be revealed underneath.
 *
 * Both are pure canvas-2D and stateless aside from particle storage.
 */

const GOLD = "#C5A46D";
const GOLD_LIGHT = "#E8D29B";
const GOLD_DARK = "#9C7E48";

// --------------------------------------------------------------------------
// Triangulated avatar
// --------------------------------------------------------------------------

interface PoseLandmark {
  x: number;
  y: number;
  visibility?: number;
}

/** Triangle definitions (indices into the MediaPipe Pose 33-landmark array). */
const TRIANGLES: [number, number, number][] = [
  // Torso front (split as two triangles)
  [11, 12, 24], // LShoulder, RShoulder, RHip
  [11, 24, 23], // LShoulder, RHip, LHip
  // Left arm
  [11, 13, 23], // LShoulder, LElbow, LHip
  [13, 15, 23], // LElbow, LWrist, LHip
  // Right arm
  [12, 14, 24], // RShoulder, RElbow, RHip
  [14, 16, 24], // RElbow, RWrist, RHip
  // Left leg upper
  [23, 25, 24], // LHip, LKnee, RHip
  [25, 27, 23], // LKnee, LAnkle, LHip
  // Right leg upper
  [24, 26, 23], // RHip, RKnee, LHip
  [26, 28, 24], // RKnee, RAnkle, RHip
  // Head triangles (face → shoulders)
  [0, 11, 12],  // Nose, LShoulder, RShoulder
];

/** Polylines (edges drawn over the mesh fill for definition). */
const POLY_LINES: [number, number][] = [
  // Outer body silhouette
  [11, 13],
  [13, 15],
  [12, 14],
  [14, 16],
  [11, 23],
  [12, 24],
  [23, 25],
  [25, 27],
  [24, 26],
  [26, 28],
  // Cross-body
  [11, 12],
  [23, 24],
  // Head
  [0, 11],
  [0, 12],
];

/** Vertex points to highlight as gold dots. */
const VERTICES = [0, 11, 12, 13, 14, 15, 16, 23, 24, 25, 26, 27, 28];

/**
 * Returns true when the given landmark array has enough confidence to render the avatar.
 */
export function isPoseUsable(lm: PoseLandmark[] | undefined): boolean {
  if (!lm || lm.length < 29) return false;
  const need = [11, 12, 23, 24];
  return need.every((i) => lm[i] && (lm[i].visibility ?? 0) > 0.3);
}

/**
 * Project a normalized landmark to canvas pixels.
 * The /tryon page mirrors video and canvas with `transform: scaleX(-1)`, so x stays normalized
 * (it gets flipped by the CSS transform).
 */
function project(lm: PoseLandmark, W: number, H: number): { x: number; y: number; v: number } {
  return { x: lm.x * W, y: lm.y * H, v: lm.visibility ?? 1 };
}

/**
 * Render a low-poly gold avatar over the user's silhouette.
 *
 * Uses semi-transparent gold fills for triangles and crisper gold strokes for the silhouette
 * so the result reads as a "couture wireframe" rather than as raw debug overlay.
 *
 * @param alpha 0–1 master alpha (allows fading the wireframe in/out between phases)
 */
export function drawTriangulatedAvatar(
  ctx: CanvasRenderingContext2D,
  landmarks: PoseLandmark[],
  W: number,
  H: number,
  alpha: number,
  pulse: number,
): void {
  if (!isPoseUsable(landmarks)) return;

  ctx.save();
  ctx.globalAlpha = alpha;

  // 1) Triangle fills with subtle gradient (top-down for body volume feel)
  const grad = ctx.createLinearGradient(0, 0, 0, H);
  grad.addColorStop(0, "rgba(232, 210, 155, 0.10)");
  grad.addColorStop(0.5, "rgba(197, 164, 109, 0.18)");
  grad.addColorStop(1, "rgba(156, 126, 72, 0.10)");

  ctx.fillStyle = grad;
  for (const [a, b, c] of TRIANGLES) {
    const A = landmarks[a];
    const B = landmarks[b];
    const C = landmarks[c];
    if (!A || !B || !C) continue;
    const va = (A.visibility ?? 0);
    const vb = (B.visibility ?? 0);
    const vc = (C.visibility ?? 0);
    if (va < 0.25 || vb < 0.25 || vc < 0.25) continue;
    const PA = project(A, W, H);
    const PB = project(B, W, H);
    const PC = project(C, W, H);
    ctx.beginPath();
    ctx.moveTo(PA.x, PA.y);
    ctx.lineTo(PB.x, PB.y);
    ctx.lineTo(PC.x, PC.y);
    ctx.closePath();
    ctx.fill();
  }

  // 2) Triangle edges (hairlines)
  ctx.strokeStyle = "rgba(232, 210, 155, 0.35)";
  ctx.lineWidth = 1;
  for (const [a, b, c] of TRIANGLES) {
    const A = landmarks[a];
    const B = landmarks[b];
    const C = landmarks[c];
    if (!A || !B || !C) continue;
    const va = (A.visibility ?? 0);
    const vb = (B.visibility ?? 0);
    const vc = (C.visibility ?? 0);
    if (va < 0.25 || vb < 0.25 || vc < 0.25) continue;
    const PA = project(A, W, H);
    const PB = project(B, W, H);
    const PC = project(C, W, H);
    ctx.beginPath();
    ctx.moveTo(PA.x, PA.y);
    ctx.lineTo(PB.x, PB.y);
    ctx.lineTo(PC.x, PC.y);
    ctx.closePath();
    ctx.stroke();
  }

  // 3) Silhouette polylines — bolder gold
  ctx.strokeStyle = GOLD;
  ctx.lineWidth = 2.5;
  ctx.lineCap = "round";
  ctx.lineJoin = "round";
  ctx.shadowColor = "rgba(232, 210, 155, 0.55)";
  ctx.shadowBlur = 8 + pulse * 6;
  for (const [a, b] of POLY_LINES) {
    const A = landmarks[a];
    const B = landmarks[b];
    if (!A || !B) continue;
    if ((A.visibility ?? 0) < 0.25 || (B.visibility ?? 0) < 0.25) continue;
    const PA = project(A, W, H);
    const PB = project(B, W, H);
    ctx.beginPath();
    ctx.moveTo(PA.x, PA.y);
    ctx.lineTo(PB.x, PB.y);
    ctx.stroke();
  }
  ctx.shadowBlur = 0;

  // 4) Vertex dots
  for (const i of VERTICES) {
    const L = landmarks[i];
    if (!L || (L.visibility ?? 0) < 0.25) continue;
    const P = project(L, W, H);
    ctx.fillStyle = GOLD_LIGHT;
    ctx.beginPath();
    ctx.arc(P.x, P.y, 3 + pulse * 1.5, 0, Math.PI * 2);
    ctx.fill();
    ctx.fillStyle = "rgba(232, 210, 155, 0.25)";
    ctx.beginPath();
    ctx.arc(P.x, P.y, 7 + pulse * 3, 0, Math.PI * 2);
    ctx.fill();
  }

  ctx.restore();
}

// --------------------------------------------------------------------------
// Body bounding box helper (for the swirl center & spread radius)
// --------------------------------------------------------------------------

export interface BodyBox {
  cx: number;
  cy: number;
  width: number;
  height: number;
}

export function bodyBox(landmarks: PoseLandmark[] | undefined, W: number, H: number): BodyBox | null {
  if (!isPoseUsable(landmarks)) return null;
  const idx = [0, 11, 12, 23, 24, 25, 26, 27, 28];
  let minX = Infinity, minY = Infinity, maxX = -Infinity, maxY = -Infinity;
  for (const i of idx) {
    const L = landmarks![i];
    if (!L || (L.visibility ?? 0) < 0.3) continue;
    const x = L.x * W;
    const y = L.y * H;
    if (x < minX) minX = x;
    if (y < minY) minY = y;
    if (x > maxX) maxX = x;
    if (y > maxY) maxY = y;
  }
  if (!isFinite(minX)) return null;
  return {
    cx: (minX + maxX) / 2,
    cy: (minY + maxY) / 2,
    width: maxX - minX,
    height: maxY - minY,
  };
}

// --------------------------------------------------------------------------
// Golden Swirl particle system
// --------------------------------------------------------------------------

interface Particle {
  /** angle around body center (radians) */
  theta: number;
  /** radial distance from center */
  r: number;
  /** vertical position relative to body center (px) */
  yOff: number;
  /** angular velocity */
  omega: number;
  /** vertical velocity */
  vy: number;
  /** life 0..1 */
  life: number;
  /** total lifetime in frames */
  ttl: number;
  size: number;
  hueShift: number;
}

export class GoldenSwirl {
  private particles: Particle[] = [];
  private startedAt = 0;
  /** progress 0..1 of the swirl phase */
  public progress = 0;

  constructor(private capacity: number = 260) {}

  reset(): void {
    this.particles = [];
    this.startedAt = 0;
    this.progress = 0;
  }

  start(now: number): void {
    this.particles = [];
    this.startedAt = now;
    this.progress = 0;
  }

  /**
   * Update + render the swirl over the given body box. Returns the current envelope value
   * (0..1) — the fraction of the box covered by particles.
   *
   * @param now performance.now() timestamp
   * @param duration target swirl duration (ms)
   */
  update(
    ctx: CanvasRenderingContext2D,
    body: BodyBox,
    now: number,
    duration: number,
  ): number {
    if (this.startedAt === 0) this.startedAt = now;
    const elapsed = now - this.startedAt;
    const tNorm = Math.min(1, elapsed / duration);
    this.progress = tNorm;

    // Spawn rate ramps up then ramps down (bell curve)
    const spawnIntensity = Math.sin(Math.PI * tNorm); // 0→1→0
    const targetCount = Math.floor(this.capacity * Math.min(1, tNorm * 1.6));
    while (this.particles.length < targetCount) {
      const fromBelow = Math.random() < 0.45;
      const baseR = body.width * (0.55 + Math.random() * 0.35);
      this.particles.push({
        theta: Math.random() * Math.PI * 2,
        r: baseR * (1.1 + Math.random() * 0.5),
        yOff: fromBelow
          ? body.height * 0.5 + Math.random() * 60
          : (Math.random() - 0.5) * body.height,
        omega: (0.025 + Math.random() * 0.04) * (Math.random() < 0.5 ? -1 : 1),
        vy: fromBelow ? -(0.6 + Math.random() * 1.2) : (Math.random() - 0.5) * 0.6,
        life: 0,
        ttl: 80 + Math.random() * 80,
        size: 1 + Math.random() * 2.6,
        hueShift: Math.random() * 0.3,
      });
    }

    ctx.save();
    ctx.globalCompositeOperation = "lighter";

    const targetR = body.width * 0.32; // particles converge to this radius (clinging to body)
    const survive: Particle[] = [];
    for (const p of this.particles) {
      // Update
      p.life += 1 / p.ttl;
      p.theta += p.omega * (1 + tNorm * 1.5);
      // Radial inward acceleration (more during second half)
      const inward = 0.018 + tNorm * 0.05;
      p.r += (targetR - p.r) * inward;
      p.yOff += p.vy;
      p.vy *= 0.985;

      // Fade in then fade out by life
      const fadeIn = Math.min(1, p.life * 4);
      const fadeOut = 1 - Math.max(0, (p.life - 0.6) / 0.4);
      const alpha =
        Math.max(0, Math.min(1, fadeIn * fadeOut)) * (0.55 + 0.45 * spawnIntensity);

      if (p.life >= 1) continue;

      // Project to canvas
      const x = body.cx + Math.cos(p.theta) * p.r;
      const y = body.cy + p.yOff + Math.sin(p.theta) * p.r * 0.35;

      // Sparkle: small bright core + soft halo
      const r = p.size * (1 + 0.3 * Math.sin(now * 0.02 + p.theta));
      const halo = ctx.createRadialGradient(x, y, 0, x, y, r * 5);
      const hue = p.hueShift > 0.15 ? GOLD_LIGHT : GOLD;
      halo.addColorStop(0, hue);
      halo.addColorStop(0.4, "rgba(232, 210, 155, 0.5)");
      halo.addColorStop(1, "rgba(232, 210, 155, 0)");
      ctx.globalAlpha = alpha;
      ctx.fillStyle = halo;
      ctx.beginPath();
      ctx.arc(x, y, r * 5, 0, Math.PI * 2);
      ctx.fill();

      // Bright core
      ctx.globalAlpha = alpha;
      ctx.fillStyle = GOLD_LIGHT;
      ctx.beginPath();
      ctx.arc(x, y, r * 0.9, 0, Math.PI * 2);
      ctx.fill();

      // Streak (motion trail) — faint line opposite to omega
      ctx.globalAlpha = alpha * 0.4;
      ctx.strokeStyle = GOLD_DARK;
      ctx.lineWidth = 0.6;
      ctx.beginPath();
      const trailLen = 6 + tNorm * 8;
      const tx = x - Math.cos(p.theta + Math.PI / 2) * trailLen * Math.sign(p.omega);
      const ty = y - Math.sin(p.theta + Math.PI / 2) * trailLen * Math.sign(p.omega);
      ctx.moveTo(x, y);
      ctx.lineTo(tx, ty);
      ctx.stroke();

      survive.push(p);
    }
    this.particles = survive;

    // Body-shaped bloom (soft enveloping aura) — grows as the swirl envelopes the body
    const bloomR = Math.min(body.width, body.height) * (0.55 + tNorm * 0.35);
    const bloom = ctx.createRadialGradient(
      body.cx,
      body.cy,
      bloomR * 0.1,
      body.cx,
      body.cy,
      bloomR,
    );
    bloom.addColorStop(0, `rgba(232, 210, 155, ${0.05 + tNorm * 0.18})`);
    bloom.addColorStop(0.6, `rgba(197, 164, 109, ${0.03 + tNorm * 0.12})`);
    bloom.addColorStop(1, "rgba(0, 0, 0, 0)");
    ctx.globalAlpha = 1;
    ctx.fillStyle = bloom;
    ctx.beginPath();
    ctx.arc(body.cx, body.cy, bloomR, 0, Math.PI * 2);
    ctx.fill();

    ctx.restore();
    return tNorm;
  }
}

// --------------------------------------------------------------------------
// Smooth easing
// --------------------------------------------------------------------------

export function easeOutCubic(t: number): number {
  return 1 - Math.pow(1 - t, 3);
}

export function easeInOutCubic(t: number): number {
  return t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2;
}
