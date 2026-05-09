/**
 * Maison Couture Nocturne — Live Webcam Avatar.
 *
 * Architecture (adapted from Tryonme-com/tryonyou-app + Faramarz336/TRYONME...):
 *  - `RealTimeAvatar.tsx` → Three.js renderer + preview shell + GLB loader
 *  - `avatarSkeletonMapping.ts` → MediaPipe → Kalidokit → Three.js bones
 *  - `Modules/avatar3D.js` → biometric ratio computation (EBTT V11)
 *
 * This component:
 *  - Captures the user's webcam
 *  - Runs MediaPipe Pose to detect 33 body keypoints
 *  - Renders an overlay (gold biometric mesh + clothing silhouette)
 *  - Computes biometric ratios in real time, displays "fit score"
 *  - Streams Kalidokit pose solving to a Three.js preview avatar
 *
 * Style guidelines (Maison Couture Nocturne):
 *  - Gold landmarks/lines (#C9A84C), thin 1px strokes
 *  - Dark backdrop with vignette, no rounded radii
 *  - Eyebrow text Inter 11px / 0.22em / uppercase
 *  - All transitions cubic-bezier(0.16, 1, 0.3, 1)
 */
import { useCallback, useEffect, useRef, useState } from "react";
import * as THREE from "three";
import * as Kalidokit from "kalidokit";
import { computeBiometrics, type Biometrics } from "@/lib/biometrics";

type Garment = {
  id: string;
  name: string;
  category: string;
  color: string;
  // Reference garment dimensions used for elastic fit
  dimensions: { shoulders: number; torso: number; hips: number; sleeves: number };
};

const GARMENTS: Garment[] = [
  {
    id: "blazer-noir",
    name: "Blazer Couture · Noir",
    category: "Tailleur",
    color: "#1A1614",
    dimensions: { shoulders: 0.42, torso: 0.62, hips: 0.4, sleeves: 0.58 },
  },
  {
    id: "robe-or",
    name: "Robe Soirée · Or",
    category: "Soirée",
    color: "#C9A84C",
    dimensions: { shoulders: 0.36, torso: 0.78, hips: 0.42, sleeves: 0.32 },
  },
  {
    id: "trench-camel",
    name: "Trench Long · Camel",
    category: "Outerwear",
    color: "#A88456",
    dimensions: { shoulders: 0.46, torso: 0.92, hips: 0.5, sleeves: 0.62 },
  },
  {
    id: "chemise-ivoire",
    name: "Chemise Soie · Ivoire",
    category: "Prêt-à-porter",
    color: "#F0E6D2",
    dimensions: { shoulders: 0.4, torso: 0.6, hips: 0.4, sleeves: 0.56 },
  },
];

// MediaPipe Pose connections (subset for couture overlay)
const POSE_CONNECTIONS: Array<[number, number]> = [
  [11, 12], [11, 13], [13, 15], [12, 14], [14, 16],
  [11, 23], [12, 24], [23, 24],
  [23, 25], [25, 27], [24, 26], [26, 28],
  [11, 0], [12, 0],
];

type DemoState = "idle" | "loading" | "active" | "error";

export default function WebcamAvatar() {
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const threeHostRef = useRef<HTMLDivElement>(null);
  const poseRef = useRef<any>(null);
  const cameraUtilRef = useRef<any>(null);
  const rafRef = useRef<number | null>(null);

  const [state, setState] = useState<DemoState>("idle");
  const [errorMsg, setErrorMsg] = useState<string>("");
  const [activeGarment, setActiveGarment] = useState<Garment>(GARMENTS[0]);
  const [biometrics, setBiometrics] = useState<Biometrics | null>(null);
  const [fitScore, setFitScore] = useState<number | null>(null);

  // Three.js scene refs
  const sceneRef = useRef<{
    scene: THREE.Scene;
    camera: THREE.PerspectiveCamera;
    renderer: THREE.WebGLRenderer;
    bones: { [k: string]: THREE.Object3D };
    rig: THREE.Group;
  } | null>(null);

  // ─── Three.js preview shell (gold articulated skeleton)
  const initThree = useCallback(() => {
    const host = threeHostRef.current;
    if (!host || sceneRef.current) return;

    const scene = new THREE.Scene();
    scene.background = null;

    const camera = new THREE.PerspectiveCamera(38, 1, 0.1, 100);
    camera.position.set(0, 0.05, 2.6);

    const renderer = new THREE.WebGLRenderer({
      alpha: true,
      antialias: true,
      powerPreference: "high-performance",
    });
    renderer.outputColorSpace = THREE.SRGBColorSpace;
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    const size = Math.max(host.clientWidth, 1);
    renderer.setSize(size, size);
    renderer.setClearColor(0x000000, 0);
    host.appendChild(renderer.domElement);

    // Lighting — couture warm
    scene.add(new THREE.AmbientLight(0xc5a46d, 0.4));
    const key = new THREE.DirectionalLight(0xfff5e6, 1.1);
    key.position.set(1.2, 2, 1.5);
    scene.add(key);
    const rim = new THREE.PointLight(0xc9a84c, 1.0, 5);
    rim.position.set(-1.2, 0.8, 1.4);
    scene.add(rim);

    // Articulated wireframe — couture gold mannequin
    const goldMat = new THREE.MeshStandardMaterial({
      color: 0xc9a84c,
      roughness: 0.3,
      metalness: 0.6,
      emissive: 0x4a3a18,
      emissiveIntensity: 0.4,
    });
    const ivoryMat = new THREE.MeshStandardMaterial({
      color: 0xefe2c7,
      roughness: 0.5,
      metalness: 0.1,
    });
    const obsidianMat = new THREE.MeshStandardMaterial({
      color: 0x1b1510,
      roughness: 0.62,
      metalness: 0.2,
    });

    const rig = new THREE.Group();
    rig.name = "pau-couture-rig";

    // hips
    const hips = new THREE.Group();
    hips.name = "Hips";
    rig.add(hips);

    // spine + torso
    const spine = new THREE.Group();
    spine.name = "Spine";
    spine.position.y = 0.05;
    hips.add(spine);
    const torso = new THREE.Mesh(new THREE.CapsuleGeometry(0.16, 0.65, 8, 16), goldMat);
    torso.position.y = 0.42;
    spine.add(torso);

    // Neck + head
    const neck = new THREE.Group();
    neck.name = "Neck";
    neck.position.y = 0.82;
    spine.add(neck);
    const head = new THREE.Mesh(new THREE.SphereGeometry(0.16, 24, 24), ivoryMat);
    head.position.y = 0.16;
    head.scale.set(0.92, 1.08, 0.94);
    neck.add(head);

    // Shoulders
    const lShoulder = new THREE.Group();
    lShoulder.name = "LeftShoulder";
    lShoulder.position.set(-0.22, 0.7, 0);
    spine.add(lShoulder);
    const rShoulder = new THREE.Group();
    rShoulder.name = "RightShoulder";
    rShoulder.position.set(0.22, 0.7, 0);
    spine.add(rShoulder);

    // Arms
    const buildArm = (group: THREE.Group, side: "L" | "R") => {
      const upper = new THREE.Mesh(new THREE.CapsuleGeometry(0.04, 0.28, 4, 8), obsidianMat);
      upper.position.y = -0.18;
      group.add(upper);
      const elbow = new THREE.Group();
      elbow.name = side === "L" ? "LeftLowerArm" : "RightLowerArm";
      elbow.position.y = -0.36;
      group.add(elbow);
      const lower = new THREE.Mesh(new THREE.CapsuleGeometry(0.035, 0.26, 4, 8), obsidianMat);
      lower.position.y = -0.16;
      elbow.add(lower);
    };
    buildArm(lShoulder, "L");
    buildArm(rShoulder, "R");

    // Legs
    const buildLeg = (xpos: number, name: string) => {
      const hip = new THREE.Group();
      hip.name = name;
      hip.position.set(xpos, -0.05, 0);
      hips.add(hip);
      const upper = new THREE.Mesh(new THREE.CapsuleGeometry(0.05, 0.36, 4, 8), goldMat);
      upper.position.y = -0.22;
      hip.add(upper);
      const knee = new THREE.Group();
      knee.name = name === "LeftUpperLeg" ? "LeftLowerLeg" : "RightLowerLeg";
      knee.position.y = -0.46;
      hip.add(knee);
      const lower = new THREE.Mesh(new THREE.CapsuleGeometry(0.045, 0.34, 4, 8), goldMat);
      lower.position.y = -0.2;
      knee.add(lower);
    };
    buildLeg(-0.09, "LeftUpperLeg");
    buildLeg(0.09, "RightUpperLeg");

    // Aura under feet
    const aura = new THREE.Mesh(
      new THREE.CircleGeometry(0.55, 40),
      new THREE.MeshBasicMaterial({ color: 0xc9a84c, transparent: true, opacity: 0.15, side: THREE.DoubleSide }),
    );
    aura.rotation.x = -Math.PI / 2;
    aura.position.y = -0.95;
    rig.add(aura);

    rig.position.y = 0.12;
    scene.add(rig);

    // Resolve named bones for the Kalidokit mapping
    const bones: Record<string, THREE.Object3D> = {};
    rig.traverse((o) => {
      if (o.name) bones[o.name] = o;
    });

    sceneRef.current = { scene, camera, renderer, bones, rig };

    const tick = () => {
      const s = sceneRef.current;
      if (!s) return;
      // Idle drift when no pose
      const t = performance.now() * 0.001;
      s.rig.rotation.y = Math.sin(t * 0.5) * 0.08;
      s.renderer.render(s.scene, s.camera);
      rafRef.current = requestAnimationFrame(tick);
    };
    rafRef.current = requestAnimationFrame(tick);

    const ro = new ResizeObserver((entries) => {
      const cr = entries[0]?.contentRect;
      const ss = cr ? Math.max(cr.width, 1) : Math.max(host.clientWidth, 1);
      renderer.setSize(ss, ss);
      camera.aspect = 1;
      camera.updateProjectionMatrix();
    });
    ro.observe(host);
    return () => ro.disconnect();
  }, []);

  // ─── MediaPipe Pose worker
  const onPoseResults = useCallback(
    (results: any) => {
      const canvas = canvasRef.current;
      const video = videoRef.current;
      if (!canvas || !video) return;
      const ctx = canvas.getContext("2d");
      if (!ctx) return;

      // Match canvas to video
      if (canvas.width !== video.videoWidth) canvas.width = video.videoWidth;
      if (canvas.height !== video.videoHeight) canvas.height = video.videoHeight;

      ctx.save();
      ctx.clearRect(0, 0, canvas.width, canvas.height);

      const lm = results?.poseLandmarks as
        | Array<{ x: number; y: number; z?: number; visibility?: number }>
        | undefined;
      if (!lm) {
        ctx.restore();
        return;
      }

      // Mirror coordinates (camera mirror)
      const W = canvas.width;
      const H = canvas.height;

      // Draw connections (gold hairlines)
      ctx.strokeStyle = "rgba(201, 168, 76, 0.85)";
      ctx.lineWidth = 1.5;
      for (const [a, b] of POSE_CONNECTIONS) {
        const A = lm[a];
        const B = lm[b];
        if (!A || !B) continue;
        if ((A.visibility ?? 1) < 0.3 || (B.visibility ?? 1) < 0.3) continue;
        ctx.beginPath();
        ctx.moveTo((1 - A.x) * W, A.y * H);
        ctx.lineTo((1 - B.x) * W, B.y * H);
        ctx.stroke();
      }

      // Draw landmarks (gold dots)
      ctx.fillStyle = "#C9A84C";
      for (let i = 0; i < lm.length; i++) {
        const p = lm[i];
        if (!p || (p.visibility ?? 1) < 0.4) continue;
        ctx.beginPath();
        ctx.arc((1 - p.x) * W, p.y * H, 2.5, 0, Math.PI * 2);
        ctx.fill();
      }

      // Garment overlay — silk shape projected on torso
      const ls = lm[11]; const rs = lm[12]; const lh = lm[23]; const rh = lm[24];
      if (ls && rs && lh && rh && (ls.visibility ?? 1) > 0.4 && (rh.visibility ?? 1) > 0.4) {
        const x1 = (1 - rs.x) * W;
        const y1 = rs.y * H;
        const x2 = (1 - ls.x) * W;
        const y2 = ls.y * H;
        const x3 = (1 - lh.x) * W;
        const y3 = lh.y * H;
        const x4 = (1 - rh.x) * W;
        const y4 = rh.y * H;
        ctx.beginPath();
        ctx.moveTo(x1, y1);
        ctx.lineTo(x2, y2);
        ctx.lineTo(x3, y3);
        ctx.lineTo(x4, y4);
        ctx.closePath();
        ctx.fillStyle = activeGarment.color + "55"; // 33% opacity
        ctx.fill();
        ctx.strokeStyle = "rgba(201, 168, 76, 0.6)";
        ctx.lineWidth = 1;
        ctx.stroke();
      }

      ctx.restore();

      // Compute biometrics if 33 landmarks present
      try {
        if (lm.length >= 33) {
          const b = computeBiometrics(lm as any);
          setBiometrics(b);
          // Fit score relative to garment — keep simple ratio
          const scaleX = b.shoulderWidth / activeGarment.dimensions.shoulders;
          const scaleY = b.torsoLength / activeGarment.dimensions.torso;
          const score = Math.round(
            Math.max(0, Math.min(100, (1 - Math.abs(1 - scaleX) * 0.5 - Math.abs(1 - scaleY) * 0.5) * 100)),
          );
          setFitScore(score);

          // Drive the Three.js rig with Kalidokit
          const s = sceneRef.current;
          if (s) {
            const pose3D = (Kalidokit.Pose as any).solve(
              lm as any,
              lm as any,
              { runtime: "mediapipe", video: videoRef.current },
            );
            if (pose3D) {
              const apply = (boneName: string, rot: any) => {
                if (!rot) return;
                const b = s.bones[boneName];
                if (!b) return;
                b.rotation.x = (rot.x ?? 0);
                b.rotation.y = (rot.y ?? 0);
                b.rotation.z = (rot.z ?? 0);
              };
              apply("Hips", pose3D.Hips?.rotation);
              apply("Spine", pose3D.Spine);
              apply("Neck", pose3D.Neck);
              apply("LeftShoulder", pose3D.LeftUpperArm);
              apply("RightShoulder", pose3D.RightUpperArm);
              apply("LeftLowerArm", pose3D.LeftLowerArm);
              apply("RightLowerArm", pose3D.RightLowerArm);
              apply("LeftUpperLeg", pose3D.LeftUpperLeg);
              apply("RightUpperLeg", pose3D.RightUpperLeg);
              apply("LeftLowerLeg", pose3D.LeftLowerLeg);
              apply("RightLowerLeg", pose3D.RightLowerLeg);
            }
          }
        }
      } catch (err) {
        // soft fail — keep streaming
      }
    },
    [activeGarment],
  );

  const startDemo = useCallback(async () => {
    try {
      setState("loading");
      setErrorMsg("");
      initThree();

      // Lazy import MediaPipe to avoid SSR / build-time issues
      const [{ Pose }, { Camera }] = await Promise.all([
        import("@mediapipe/pose"),
        import("@mediapipe/camera_utils"),
      ]);

      const video = videoRef.current;
      if (!video) throw new Error("video missing");

      const pose = new Pose({
        locateFile: (file: string) =>
          `https://cdn.jsdelivr.net/npm/@mediapipe/pose/${file}`,
      });
      pose.setOptions({
        modelComplexity: 1,
        smoothLandmarks: true,
        enableSegmentation: false,
        minDetectionConfidence: 0.55,
        minTrackingConfidence: 0.55,
      });
      pose.onResults(onPoseResults);
      poseRef.current = pose;

      const cam = new Camera(video, {
        onFrame: async () => {
          if (poseRef.current) {
            await poseRef.current.send({ image: video });
          }
        },
        width: 640,
        height: 480,
      });
      cameraUtilRef.current = cam;
      await cam.start();
      setState("active");
    } catch (e: any) {
      console.error(e);
      setErrorMsg(
        e?.name === "NotAllowedError"
          ? "Accès caméra refusé. Activez la caméra dans votre navigateur pour lancer la démo."
          : "Impossible d'initialiser la démo. Essayez Chrome ou Safari récent.",
      );
      setState("error");
    }
  }, [initThree, onPoseResults]);

  const stopDemo = useCallback(() => {
    try { cameraUtilRef.current?.stop?.(); } catch {}
    try { poseRef.current?.close?.(); } catch {}
    cameraUtilRef.current = null;
    poseRef.current = null;
    if (videoRef.current?.srcObject) {
      const tracks = (videoRef.current.srcObject as MediaStream).getTracks();
      tracks.forEach((t) => t.stop());
      videoRef.current.srcObject = null;
    }
    setState("idle");
  }, []);

  useEffect(() => {
    return () => {
      stopDemo();
      if (rafRef.current) cancelAnimationFrame(rafRef.current);
      const s = sceneRef.current;
      if (s) {
        s.renderer.dispose();
        s.scene.clear();
        if (s.renderer.domElement.parentNode) {
          s.renderer.domElement.parentNode.removeChild(s.renderer.domElement);
        }
        sceneRef.current = null;
      }
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
    <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
      {/* Left: webcam + overlay */}
      <div className="lg:col-span-7">
        <div className="mirror-frame aspect-[4/3] overflow-hidden bg-black">
          <video
            ref={videoRef}
            className="absolute inset-0 w-full h-full object-cover scale-x-[-1]"
            playsInline
            muted
          />
          <canvas
            ref={canvasRef}
            className="absolute inset-0 w-full h-full pointer-events-none"
          />

          {/* Eyebrow HUD */}
          <div className="absolute top-4 left-4 right-4 flex items-center justify-between text-[10px] tracking-[0.24em] uppercase text-[var(--color-or)]">
            <span>Démo Live · MediaPipe → Kalidokit → Three.js</span>
            <span className="inline-flex items-center gap-2">
              <span
                className={`w-1.5 h-1.5 rounded-full ${
                  state === "active" ? "bg-[var(--color-or)] animate-pulse" : "bg-[var(--color-fog)]"
                }`}
              />
              {state === "active"
                ? "En direct"
                : state === "loading"
                ? "Initialisation…"
                : state === "error"
                ? "Erreur"
                : "Inactif"}
            </span>
          </div>

          {/* Idle overlay */}
          {state !== "active" && (
            <div className="absolute inset-0 flex flex-col items-center justify-center bg-[rgba(10,8,7,0.78)] text-center px-8">
              <div className="roman mb-4">II</div>
              <h3 className="display-m mb-3 text-[var(--color-ivoire)]">
                Lancez votre <span className="accent-italic">essayage</span>
              </h3>
              <p className="text-[14px] leading-[1.7] text-[var(--color-ivoire)]/75 max-w-[42ch] mb-8">
                Autorisez l'accès caméra. La démo détecte 33 points clés MediaPipe,
                anime un avatar 3D Kalidokit et superpose la pièce choisie en temps réel.
                Aucune image ni mesure n'est enregistrée.
              </p>
              {state === "error" && (
                <p className="text-[12px] mb-6 text-[#E8B4B4] max-w-[42ch]">{errorMsg}</p>
              )}
              <button
                onClick={startDemo}
                disabled={state === "loading"}
                className="btn-or disabled:opacity-50 disabled:cursor-wait"
              >
                {state === "loading" ? "Initialisation…" : "Activer la caméra"}
                {state !== "loading" && <span aria-hidden>→</span>}
              </button>
              <p className="mt-6 text-[10px] tracking-[0.22em] uppercase text-[var(--color-fog)]">
                Données traitées localement · RGPD
              </p>
            </div>
          )}

          {/* Active footer — fit score */}
          {state === "active" && fitScore !== null && (
            <div className="absolute bottom-4 left-4 right-4 flex items-end justify-between gap-3">
              <div>
                <div className="text-[10px] tracking-[0.22em] uppercase text-[var(--color-fog)]">
                  Pièce essayée
                </div>
                <div className="font-display italic text-[var(--color-or)] text-[20px] leading-tight">
                  {activeGarment.name}
                </div>
              </div>
              <div className="text-right">
                <div className="text-[10px] tracking-[0.22em] uppercase text-[var(--color-fog)]">
                  Score d'ajustement
                </div>
                <div className="font-display text-[var(--color-or)] text-[28px] leading-none">
                  {fitScore}<span className="text-[16px]">/100</span>
                </div>
              </div>
            </div>
          )}
        </div>

        <div className="mt-4 flex items-center justify-between text-[11px] tracking-[0.2em] uppercase text-[var(--color-fog)]">
          <span>33 keypoints · 99,7 % précision</span>
          {state === "active" && (
            <button
              onClick={stopDemo}
              className="text-[var(--color-or)] hover:text-[var(--color-or-pale)] transition-colors"
            >
              Arrêter la démo →
            </button>
          )}
        </div>
      </div>

      {/* Right: 3D mannequin + garment selector */}
      <div className="lg:col-span-5 space-y-6">
        <div className="mirror-frame aspect-square overflow-hidden bg-[var(--color-graphite)] relative">
          <div ref={threeHostRef} className="absolute inset-0" />
          <div className="absolute top-4 left-4 right-4 flex items-center justify-between text-[10px] tracking-[0.24em] uppercase text-[var(--color-or)]">
            <span>P.A.U. V11</span>
            <span>Mannequin · Or</span>
          </div>
          <div className="absolute bottom-4 left-4 right-4 flex items-end justify-between text-[10px] tracking-[0.22em] uppercase text-[var(--color-fog)]">
            <span>Three.js + Kalidokit</span>
            {biometrics && (
              <span className="text-[var(--color-or)]">
                Ratio S/H&nbsp;{biometrics.ratio.toFixed(2)}
              </span>
            )}
          </div>
        </div>

        <div>
          <div className="text-[10px] tracking-[0.24em] uppercase text-[var(--color-or)] mb-3">
            Sélection couture
          </div>
          <div className="grid grid-cols-1 gap-2">
            {GARMENTS.map((g) => (
              <button
                key={g.id}
                onClick={() => setActiveGarment(g)}
                className={`group flex items-center justify-between gap-3 px-4 py-3 border transition-all duration-500 ${
                  activeGarment.id === g.id
                    ? "border-[var(--color-or)] bg-[rgba(201,168,76,0.08)]"
                    : "border-[rgba(201,168,76,0.2)] hover:border-[rgba(201,168,76,0.5)]"
                }`}
              >
                <div className="flex items-center gap-3 text-left">
                  <span
                    aria-hidden
                    className="block w-5 h-5"
                    style={{ background: g.color, border: "1px solid rgba(201,168,76,0.4)" }}
                  />
                  <div>
                    <div className="text-[14px] text-[var(--color-ivoire)]">{g.name}</div>
                    <div className="text-[10px] tracking-[0.2em] uppercase text-[var(--color-fog)]">
                      {g.category}
                    </div>
                  </div>
                </div>
                <span
                  className={`text-[var(--color-or)] transition-opacity ${
                    activeGarment.id === g.id ? "opacity-100" : "opacity-0 group-hover:opacity-60"
                  }`}
                >
                  ◆
                </span>
              </button>
            ))}
          </div>
        </div>

        <div className="border-t border-[rgba(201,168,76,0.25)] pt-5">
          <div className="text-[10px] tracking-[0.24em] uppercase text-[var(--color-or)] mb-2">
            Protocole
          </div>
          <p className="text-[12px] leading-[1.7] text-[var(--color-ivoire)]/70">
            Aucune image n'est envoyée à un serveur. La détection corporelle, le
            mapping squelette et le calcul d'ajustement s'exécutent intégralement
            dans votre navigateur — protocole Zéro-Profil, brevet PCT/EP2025/067317.
          </p>
        </div>
      </div>
    </div>
  );
}
