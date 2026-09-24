/**
 * Cloth Physics Engine — Verlet Integration for Real-Time Fabric Drape Simulation.
 *
 * Implements a particle-spring system that simulates fabric behavior:
 * - Gravity, wind, and body collision
 * - Structural, shear, and bend constraints
 * - Verlet integration for stable, framerate-independent simulation
 *
 * Based on Thomas Jakobsen's "Advanced Character Physics" (GDC 2001)
 * and extended with fabric-specific material properties (elasticity, stiffness, damping).
 *
 * Patent PCT/EP2025/067317 — TRYONYOU–ABVETOS–ULTRA–PLUS–ULTIMATUM
 * Module: Fabric Fit Comparator — Physics-Driven Drape Intelligence
 */

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

/** 2D vector for physics calculations. */
export interface Vec2 {
  x: number;
  y: number;
}

/** A particle in the cloth mesh. */
export interface ClothParticle {
  pos: Vec2;
  prevPos: Vec2;
  acceleration: Vec2;
  mass: number;
  pinned: boolean;
  /** UV coordinate for texture mapping (0..1). */
  u: number;
  v: number;
}

/** A constraint (spring) between two particles. */
export interface ClothConstraint {
  p1Index: number;
  p2Index: number;
  restLength: number;
  stiffness: number;
  type: "structural" | "shear" | "bend";
}

/** Material properties defining fabric behavior. */
export interface FabricMaterial {
  /** Name identifier. */
  name: string;
  /** Structural stiffness (0..1). Higher = less stretch. */
  structuralStiffness: number;
  /** Shear stiffness (0..1). Higher = less diagonal deformation. */
  shearStiffness: number;
  /** Bend stiffness (0..1). Higher = stiffer fabric (denim vs silk). */
  bendStiffness: number;
  /** Damping factor (0..1). Higher = less oscillation. */
  damping: number;
  /** Mass per particle. Heavier fabrics drape more. */
  particleMass: number;
  /** Gravity multiplier. */
  gravityScale: number;
}

/** Body collision shape derived from pose landmarks. */
export interface BodyCollider {
  /** Shoulder center position (canvas pixels). */
  shoulderCenter: Vec2;
  /** Torso capsule: top (shoulders) to bottom (hips). */
  torsoTop: Vec2;
  torsoBottom: Vec2;
  /** Approximate torso radius for collision. */
  torsoRadius: number;
  /** Shoulder width for garment anchoring. */
  shoulderWidth: number;
}

/** Complete cloth simulation state. */
export interface ClothState {
  particles: ClothParticle[];
  constraints: ClothConstraint[];
  cols: number;
  rows: number;
  material: FabricMaterial;
}

/** External forces applied to the simulation. */
export interface ExternalForces {
  gravity: Vec2;
  wind: Vec2;
  /** Body collider for collision response. */
  body: BodyCollider | null;
}

// ---------------------------------------------------------------------------
// Predefined Materials — Science-Based Fabric Properties
// ---------------------------------------------------------------------------

/**
 * Material library based on real textile physics:
 * - Silk: low stiffness, low mass, high drape
 * - Cotton: medium stiffness, medium mass
 * - Wool: high stiffness, high mass, structured
 * - Denim: very high stiffness, heavy, minimal drape
 * - Neoprene: high stiffness, very structured (Balmain signature)
 * - Tweed: high stiffness, textured, structured (Balmain heritage)
 */
export const FABRIC_MATERIALS: Record<string, FabricMaterial> = {
  silk: {
    name: "Silk",
    structuralStiffness: 0.85,
    shearStiffness: 0.3,
    bendStiffness: 0.1,
    damping: 0.97,
    particleMass: 0.8,
    gravityScale: 1.2,
  },
  cotton: {
    name: "Cotton",
    structuralStiffness: 0.92,
    shearStiffness: 0.5,
    bendStiffness: 0.35,
    damping: 0.95,
    particleMass: 1.0,
    gravityScale: 1.0,
  },
  wool: {
    name: "Wool",
    structuralStiffness: 0.95,
    shearStiffness: 0.7,
    bendStiffness: 0.6,
    damping: 0.93,
    particleMass: 1.4,
    gravityScale: 0.9,
  },
  denim: {
    name: "Denim",
    structuralStiffness: 0.98,
    shearStiffness: 0.85,
    bendStiffness: 0.8,
    damping: 0.9,
    particleMass: 1.8,
    gravityScale: 0.85,
  },
  neoprene: {
    name: "Neoprene Satin",
    structuralStiffness: 0.97,
    shearStiffness: 0.9,
    bendStiffness: 0.75,
    damping: 0.88,
    particleMass: 1.6,
    gravityScale: 0.8,
  },
  tweed: {
    name: "Tweed Bouclé",
    structuralStiffness: 0.96,
    shearStiffness: 0.82,
    bendStiffness: 0.7,
    damping: 0.91,
    particleMass: 1.5,
    gravityScale: 0.88,
  },
  organza: {
    name: "Organza",
    structuralStiffness: 0.88,
    shearStiffness: 0.25,
    bendStiffness: 0.05,
    damping: 0.98,
    particleMass: 0.5,
    gravityScale: 1.4,
  },
  leather: {
    name: "Leather",
    structuralStiffness: 0.99,
    shearStiffness: 0.92,
    bendStiffness: 0.88,
    damping: 0.85,
    particleMass: 2.0,
    gravityScale: 0.75,
  },
};

// ---------------------------------------------------------------------------
// Cloth Initialization
// ---------------------------------------------------------------------------

/**
 * Creates a cloth mesh grid with particles and constraints.
 *
 * @param cols     - Number of columns in the mesh.
 * @param rows     - Number of rows in the mesh.
 * @param width    - Total width of the cloth in canvas pixels.
 * @param height   - Total height of the cloth in canvas pixels.
 * @param originX  - X origin (top-left corner of cloth).
 * @param originY  - Y origin (top-left corner of cloth).
 * @param material - Fabric material properties.
 * @param pinTop   - Whether to pin the top row (shoulder anchors).
 */
export function createClothMesh(
  cols: number,
  rows: number,
  width: number,
  height: number,
  originX: number,
  originY: number,
  material: FabricMaterial,
  pinTop = true,
): ClothState {
  const particles: ClothParticle[] = [];
  const constraints: ClothConstraint[] = [];

  const spacingX = width / (cols - 1);
  const spacingY = height / (rows - 1);

  // Create particles
  for (let row = 0; row < rows; row++) {
    for (let col = 0; col < cols; col++) {
      const x = originX + col * spacingX;
      const y = originY + row * spacingY;
      particles.push({
        pos: { x, y },
        prevPos: { x, y },
        acceleration: { x: 0, y: 0 },
        mass: material.particleMass,
        pinned: pinTop && row === 0,
        u: col / (cols - 1),
        v: row / (rows - 1),
      });
    }
  }

  // Structural constraints (horizontal + vertical neighbors)
  for (let row = 0; row < rows; row++) {
    for (let col = 0; col < cols; col++) {
      const idx = row * cols + col;

      // Horizontal
      if (col < cols - 1) {
        constraints.push({
          p1Index: idx,
          p2Index: idx + 1,
          restLength: spacingX,
          stiffness: material.structuralStiffness,
          type: "structural",
        });
      }

      // Vertical
      if (row < rows - 1) {
        constraints.push({
          p1Index: idx,
          p2Index: idx + cols,
          restLength: spacingY,
          stiffness: material.structuralStiffness,
          type: "structural",
        });
      }
    }
  }

  // Shear constraints (diagonal neighbors)
  for (let row = 0; row < rows - 1; row++) {
    for (let col = 0; col < cols - 1; col++) {
      const idx = row * cols + col;
      const diagLen = Math.hypot(spacingX, spacingY);

      // Top-left to bottom-right
      constraints.push({
        p1Index: idx,
        p2Index: idx + cols + 1,
        restLength: diagLen,
        stiffness: material.shearStiffness,
        type: "shear",
      });

      // Top-right to bottom-left
      constraints.push({
        p1Index: idx + 1,
        p2Index: idx + cols,
        restLength: diagLen,
        stiffness: material.shearStiffness,
        type: "shear",
      });
    }
  }

  // Bend constraints (skip-one neighbors for bending resistance)
  for (let row = 0; row < rows; row++) {
    for (let col = 0; col < cols; col++) {
      const idx = row * cols + col;

      // Horizontal bend
      if (col < cols - 2) {
        constraints.push({
          p1Index: idx,
          p2Index: idx + 2,
          restLength: spacingX * 2,
          stiffness: material.bendStiffness,
          type: "bend",
        });
      }

      // Vertical bend
      if (row < rows - 2) {
        constraints.push({
          p1Index: idx,
          p2Index: idx + cols * 2,
          restLength: spacingY * 2,
          stiffness: material.bendStiffness,
          type: "bend",
        });
      }
    }
  }

  return { particles, constraints, cols, rows, material };
}

// ---------------------------------------------------------------------------
// Physics Simulation Step (Verlet Integration)
// ---------------------------------------------------------------------------

/**
 * Advances the cloth simulation by one timestep using Verlet integration.
 *
 * Physics pipeline:
 * 1. Apply external forces (gravity, wind)
 * 2. Verlet integration (position update)
 * 3. Constraint satisfaction (iterative relaxation)
 * 4. Body collision response
 *
 * @param state            - Current cloth state (mutated in place).
 * @param dt               - Timestep in seconds (typically 1/60).
 * @param forces           - External forces to apply.
 * @param constraintIters  - Number of constraint relaxation iterations (higher = stiffer).
 */
export function simulateClothStep(
  state: ClothState,
  dt: number,
  forces: ExternalForces,
  constraintIters = 5,
): void {
  const { particles, constraints, material } = state;
  const dtSq = dt * dt;

  // 1. Apply forces and integrate (Verlet)
  for (const p of particles) {
    if (p.pinned) continue;

    // Accumulate forces
    p.acceleration.x = forces.gravity.x * material.gravityScale + forces.wind.x;
    p.acceleration.y = forces.gravity.y * material.gravityScale + forces.wind.y;

    // Verlet integration: newPos = 2*pos - prevPos + acc*dt²
    const newX = p.pos.x + (p.pos.x - p.prevPos.x) * material.damping + p.acceleration.x * dtSq;
    const newY = p.pos.y + (p.pos.y - p.prevPos.y) * material.damping + p.acceleration.y * dtSq;

    p.prevPos.x = p.pos.x;
    p.prevPos.y = p.pos.y;
    p.pos.x = newX;
    p.pos.y = newY;
  }

  // 2. Satisfy constraints (iterative relaxation — Jakobsen method)
  for (let iter = 0; iter < constraintIters; iter++) {
    for (const c of constraints) {
      const p1 = particles[c.p1Index];
      const p2 = particles[c.p2Index];

      const dx = p2.pos.x - p1.pos.x;
      const dy = p2.pos.y - p1.pos.y;
      const dist = Math.hypot(dx, dy);

      if (dist < 1e-6) continue;

      const diff = (dist - c.restLength) / dist;
      const correction = diff * c.stiffness * 0.5;

      const offsetX = dx * correction;
      const offsetY = dy * correction;

      if (!p1.pinned) {
        p1.pos.x += offsetX;
        p1.pos.y += offsetY;
      }
      if (!p2.pinned) {
        p2.pos.x -= offsetX;
        p2.pos.y -= offsetY;
      }
    }
  }

  // 3. Body collision (simplified torso capsule)
  if (forces.body) {
    const { torsoTop, torsoBottom, torsoRadius } = forces.body;

    for (const p of particles) {
      if (p.pinned) continue;

      // Point-to-segment distance for capsule collision
      const segDx = torsoBottom.x - torsoTop.x;
      const segDy = torsoBottom.y - torsoTop.y;
      const segLenSq = segDx * segDx + segDy * segDy;

      let t = 0;
      if (segLenSq > 1e-6) {
        t = ((p.pos.x - torsoTop.x) * segDx + (p.pos.y - torsoTop.y) * segDy) / segLenSq;
        t = Math.max(0, Math.min(1, t));
      }

      const closestX = torsoTop.x + t * segDx;
      const closestY = torsoTop.y + t * segDy;

      const toPx = p.pos.x - closestX;
      const toPy = p.pos.y - closestY;
      const distToAxis = Math.hypot(toPx, toPy);

      if (distToAxis < torsoRadius && distToAxis > 1e-6) {
        // Push particle out of body
        const pushFactor = (torsoRadius - distToAxis) / distToAxis;
        p.pos.x += toPx * pushFactor;
        p.pos.y += toPy * pushFactor;
      }
    }
  }
}

// ---------------------------------------------------------------------------
// Anchor Update (sync pinned particles with pose)
// ---------------------------------------------------------------------------

/**
 * Updates the pinned (top-row) particles to follow the user's shoulder line.
 * This creates the "hanging from shoulders" effect.
 *
 * @param state       - Cloth state.
 * @param leftAnchor  - Left shoulder position (canvas pixels).
 * @param rightAnchor - Right shoulder position (canvas pixels).
 */
export function updateClothAnchors(
  state: ClothState,
  leftAnchor: Vec2,
  rightAnchor: Vec2,
): void {
  const { particles, cols } = state;

  for (let col = 0; col < cols; col++) {
    const p = particles[col]; // Top row
    if (!p.pinned) continue;

    const t = col / (cols - 1); // 0 = left, 1 = right
    const targetX = leftAnchor.x + (rightAnchor.x - leftAnchor.x) * t;
    const targetY = leftAnchor.y + (rightAnchor.y - leftAnchor.y) * t;

    p.pos.x = targetX;
    p.pos.y = targetY;
    p.prevPos.x = targetX;
    p.prevPos.y = targetY;
  }
}

// ---------------------------------------------------------------------------
// Body Collider from Pose Landmarks
// ---------------------------------------------------------------------------

/**
 * Constructs a BodyCollider from MediaPipe Pose landmarks.
 * Uses shoulders (11, 12) and hips (23, 24) to define the torso capsule.
 *
 * @param landmarks - Array of 33 normalized pose landmarks.
 * @param canvasW   - Canvas width.
 * @param canvasH   - Canvas height.
 * @param mirrored  - Whether X is mirrored (webcam mode).
 */
export function bodyColliderFromLandmarks(
  landmarks: { x: number; y: number; visibility?: number }[],
  canvasW: number,
  canvasH: number,
  mirrored = true,
): BodyCollider | null {
  const ls = landmarks[11]; // Left shoulder
  const rs = landmarks[12]; // Right shoulder
  const lh = landmarks[23]; // Left hip
  const rh = landmarks[24]; // Right hip

  if (!ls || !rs || !lh || !rh) return null;
  if ((ls.visibility ?? 0) < 0.3 || (rs.visibility ?? 0) < 0.3) return null;

  const xFactor = mirrored ? -1 : 1;
  const xOffset = mirrored ? canvasW : 0;

  const toCanvas = (lm: { x: number; y: number }): Vec2 => ({
    x: xOffset + xFactor * lm.x * canvasW,
    y: lm.y * canvasH,
  });

  const lsC = toCanvas(ls);
  const rsC = toCanvas(rs);
  const lhC = toCanvas(lh);
  const rhC = toCanvas(rh);

  const shoulderCenter: Vec2 = {
    x: (lsC.x + rsC.x) / 2,
    y: (lsC.y + rsC.y) / 2,
  };

  const hipCenter: Vec2 = {
    x: (lhC.x + rhC.x) / 2,
    y: (lhC.y + rhC.y) / 2,
  };

  const shoulderWidth = Math.hypot(rsC.x - lsC.x, rsC.y - lsC.y);

  return {
    shoulderCenter,
    torsoTop: shoulderCenter,
    torsoBottom: hipCenter,
    torsoRadius: shoulderWidth * 0.35, // Approximate torso as 35% of shoulder width
    shoulderWidth,
  };
}

// ---------------------------------------------------------------------------
// Cloth Renderer (Canvas 2D — Textured Mesh)
// ---------------------------------------------------------------------------

/**
 * Renders the cloth mesh onto a Canvas 2D context using the garment texture.
 * Draws textured triangles by subdividing the cloth grid into triangle pairs.
 *
 * @param ctx       - Canvas 2D context.
 * @param state     - Current cloth state.
 * @param texture   - Garment texture image.
 * @param opacity   - Global opacity for the cloth render.
 * @param composite - Composite operation for fabric realism.
 */
export function renderClothMesh(
  ctx: CanvasRenderingContext2D,
  state: ClothState,
  texture: HTMLImageElement,
  opacity = 0.92,
  composite: GlobalCompositeOperation = "multiply",
): void {
  const { particles, cols, rows } = state;
  const tw = texture.naturalWidth;
  const th = texture.naturalHeight;

  ctx.save();
  ctx.globalCompositeOperation = composite;
  ctx.globalAlpha = opacity;

  // Render each quad as two triangles with texture mapping
  for (let row = 0; row < rows - 1; row++) {
    for (let col = 0; col < cols - 1; col++) {
      const i00 = row * cols + col;
      const i10 = row * cols + col + 1;
      const i01 = (row + 1) * cols + col;
      const i11 = (row + 1) * cols + col + 1;

      const p00 = particles[i00];
      const p10 = particles[i10];
      const p01 = particles[i01];
      const p11 = particles[i11];

      // Draw two triangles per quad using clip + drawImage with affine transform
      drawTexturedTriangle(ctx, texture, tw, th, p00, p10, p01);
      drawTexturedTriangle(ctx, texture, tw, th, p10, p11, p01);
    }
  }

  ctx.restore();
}

/**
 * Draws a single textured triangle using affine transformation.
 * Maps UV coordinates from the particle to the texture image.
 */
function drawTexturedTriangle(
  ctx: CanvasRenderingContext2D,
  texture: HTMLImageElement,
  tw: number,
  th: number,
  p0: ClothParticle,
  p1: ClothParticle,
  p2: ClothParticle,
): void {
  // Source texture coordinates
  const sx0 = p0.u * tw, sy0 = p0.v * th;
  const sx1 = p1.u * tw, sy1 = p1.v * th;
  const sx2 = p2.u * tw, sy2 = p2.v * th;

  // Destination canvas coordinates
  const dx0 = p0.pos.x, dy0 = p0.pos.y;
  const dx1 = p1.pos.x, dy1 = p1.pos.y;
  const dx2 = p2.pos.x, dy2 = p2.pos.y;

  // Compute affine transform matrix from source to destination
  // [a c e] [sx] = [dx]
  // [b d f] [sy]   [dy]
  //         [1 ]
  const denom = (sx1 - sx0) * (sy2 - sy0) - (sx2 - sx0) * (sy1 - sy0);
  if (Math.abs(denom) < 1e-6) return; // Degenerate triangle

  const invDenom = 1 / denom;

  const a = ((dx1 - dx0) * (sy2 - sy0) - (dx2 - dx0) * (sy1 - sy0)) * invDenom;
  const b = ((dy1 - dy0) * (sy2 - sy0) - (dy2 - dy0) * (sy1 - sy0)) * invDenom;
  const c = ((dx2 - dx0) * (sx1 - sx0) - (dx1 - dx0) * (sx2 - sx0)) * invDenom;
  const d = ((dy2 - dy0) * (sx1 - sx0) - (dy1 - dy0) * (sx2 - sx0)) * invDenom;
  const e = dx0 - a * sx0 - c * sy0;
  const f = dy0 - b * sx0 - d * sy0;

  ctx.save();

  // Clip to triangle
  ctx.beginPath();
  ctx.moveTo(dx0, dy0);
  ctx.lineTo(dx1, dy1);
  ctx.lineTo(dx2, dy2);
  ctx.closePath();
  ctx.clip();

  // Apply affine transform and draw texture
  ctx.setTransform(a, b, c, d, e, f);
  ctx.drawImage(texture, 0, 0);

  ctx.restore();
}

// ---------------------------------------------------------------------------
// High-Level Integration: Physics-Enhanced Garment Renderer
// ---------------------------------------------------------------------------

/**
 * Complete physics-enhanced garment rendering pipeline.
 * Combines pose tracking + cloth simulation + textured mesh rendering.
 *
 * Usage:
 *   const engine = new PhysicsGarmentEngine(material, 16, 24);
 *   // In animation loop:
 *   engine.update(landmarks, canvasW, canvasH, dt);
 *   engine.render(ctx, garmentTexture);
 */
export class PhysicsGarmentEngine {
  private cloth: ClothState | null = null;
  private initialized = false;
  private material: FabricMaterial;
  private cols: number;
  private rows: number;
  private windPhase = 0;

  constructor(material: FabricMaterial, cols = 16, rows = 24) {
    this.material = material;
    this.cols = cols;
    this.rows = rows;
  }

  /** Initialize or reinitialize the cloth mesh based on body dimensions. */
  private initCloth(shoulderWidth: number, garmentHeight: number, anchorY: number): void {
    const originX = -shoulderWidth * 0.6; // Slight overshoot for natural drape
    this.cloth = createClothMesh(
      this.cols,
      this.rows,
      shoulderWidth * 1.2,
      garmentHeight,
      originX,
      anchorY,
      this.material,
      true,
    );
    this.initialized = true;
  }

  /**
   * Update the physics simulation for one frame.
   *
   * @param landmarks - MediaPipe Pose landmarks (normalized).
   * @param canvasW   - Canvas width.
   * @param canvasH   - Canvas height.
   * @param dt        - Delta time in seconds.
   */
  update(
    landmarks: { x: number; y: number; visibility?: number }[],
    canvasW: number,
    canvasH: number,
    dt: number,
  ): boolean {
    const body = bodyColliderFromLandmarks(landmarks, canvasW, canvasH, true);
    if (!body) return false;

    // Initialize cloth on first valid body detection
    if (!this.initialized || !this.cloth) {
      const garmentHeight = body.shoulderWidth * 1.8; // Typical garment aspect
      this.initCloth(body.shoulderWidth, garmentHeight, body.shoulderCenter.y);
    }

    // Update shoulder anchors
    const leftAnchor: Vec2 = {
      x: body.shoulderCenter.x - body.shoulderWidth / 2,
      y: body.shoulderCenter.y,
    };
    const rightAnchor: Vec2 = {
      x: body.shoulderCenter.x + body.shoulderWidth / 2,
      y: body.shoulderCenter.y,
    };
    updateClothAnchors(this.cloth!, leftAnchor, rightAnchor);

    // Subtle wind oscillation for life-like movement
    this.windPhase += dt * 2.5;
    const windX = Math.sin(this.windPhase) * 15 + Math.sin(this.windPhase * 0.7) * 8;
    const windY = Math.cos(this.windPhase * 0.5) * 3;

    const forces: ExternalForces = {
      gravity: { x: 0, y: 980 }, // ~9.8 m/s² scaled to pixels
      wind: { x: windX, y: windY },
      body,
    };

    // Run physics step (multiple sub-steps for stability)
    const subSteps = 3;
    const subDt = dt / subSteps;
    for (let i = 0; i < subSteps; i++) {
      simulateClothStep(this.cloth!, subDt, forces, 4);
    }

    return true;
  }

  /**
   * Render the simulated cloth onto the canvas.
   *
   * @param ctx     - Canvas 2D context.
   * @param texture - Garment texture image.
   * @param glow    - Optional glow effect for high fit-score.
   */
  render(
    ctx: CanvasRenderingContext2D,
    texture: HTMLImageElement,
    glow?: { color: string; blur: number; alpha: number } | null,
  ): void {
    if (!this.cloth) return;

    // Glow pass
    if (glow && glow.alpha > 0) {
      ctx.save();
      ctx.shadowColor = glow.color;
      ctx.shadowBlur = glow.blur;
      ctx.globalAlpha = glow.alpha;
      renderClothMesh(ctx, this.cloth, texture, glow.alpha, "source-over");
      ctx.restore();
    }

    // Main textured render
    renderClothMesh(ctx, this.cloth, texture, 0.93, "multiply");
  }

  /** Reset the simulation (e.g., on garment change). */
  reset(): void {
    this.cloth = null;
    this.initialized = false;
    this.windPhase = 0;
  }

  /** Get current material. */
  getMaterial(): FabricMaterial {
    return this.material;
  }

  /** Change material (triggers soft reset). */
  setMaterial(material: FabricMaterial): void {
    this.material = material;
    this.reset();
  }
}
