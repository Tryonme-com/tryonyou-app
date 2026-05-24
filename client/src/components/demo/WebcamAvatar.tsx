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
import * as Kalidokit from "kalidokit";
import { computeBiometrics, type Biometrics } from "@/lib/biometrics";
import { setupThreeRig, type ThreeSceneRefs } from "./initThreeRig";
import { WebcamOverlay } from "./WebcamOverlay";
import { MannequinPreview } from "./MannequinPreview";
import type { Garment, DemoState } from "./types";

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
  [11, 12],
  [11, 13],
  [13, 15],
  [12, 14],
  [14, 16],
  [11, 23],
  [12, 24],
  [23, 24],
  [23, 25],
  [25, 27],
  [24, 26],
  [26, 28],
  [11, 0],
  [12, 0],
];

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

  // Using ref to ensure we don't trigger re-renders on every frame with pose results.
  const activeGarmentRef = useRef<Garment>(activeGarment);
  useEffect(() => {
    activeGarmentRef.current = activeGarment;
  }, [activeGarment]);

  // Three.js scene refs
  const sceneRef = useRef<{
    refs: ThreeSceneRefs;
    cleanup: () => void;
  } | null>(null);

  const initThree = useCallback(() => {
    const host = threeHostRef.current;
    if (!host || sceneRef.current) return;

    const { refs, cleanup } = setupThreeRig(host);
    sceneRef.current = { refs, cleanup };

    const tick = () => {
      const s = sceneRef.current?.refs;
      if (!s) return;
      // Idle drift when no pose
      const t = performance.now() * 0.001;
      s.rig.rotation.y = Math.sin(t * 0.5) * 0.08;
      s.renderer.render(s.scene, s.camera);
      rafRef.current = requestAnimationFrame(tick);
    };
    rafRef.current = requestAnimationFrame(tick);
  }, []);

  // ─── MediaPipe Pose worker
  const onPoseResults = useCallback((results: any) => {
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
    const garment = activeGarmentRef.current;
    const ls = lm[11];
    const rs = lm[12];
    const lh = lm[23];
    const rh = lm[24];
    if (
      ls &&
      rs &&
      lh &&
      rh &&
      (ls.visibility ?? 1) > 0.4 &&
      (rh.visibility ?? 1) > 0.4
    ) {
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
      ctx.fillStyle = garment.color + "55"; // 33% opacity
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
        // Note: setting state here might trigger re-renders, but keeping it
        // identical to original logic. For hyper-optimization, one could throttle this.
        setBiometrics(b);

        // Fit score relative to garment — keep simple ratio
        const scaleX = b.shoulderWidth / garment.dimensions.shoulders;
        const scaleY = b.torsoLength / garment.dimensions.torso;
        const score = Math.round(
          Math.max(
            0,
            Math.min(
              100,
              (1 - Math.abs(1 - scaleX) * 0.5 - Math.abs(1 - scaleY) * 0.5) *
                100
            )
          )
        );
        setFitScore(score);

        // Drive the Three.js rig with Kalidokit imperatively
        const s = sceneRef.current?.refs;
        if (s) {
          const pose3D = (Kalidokit.Pose as any).solve(lm as any, lm as any, {
            runtime: "mediapipe",
            video: videoRef.current,
          });
          if (pose3D) {
            const apply = (boneName: string, rot: any) => {
              if (!rot) return;
              const bObj = s.bones[boneName];
              if (!bObj) return;
              bObj.rotation.x = rot.x ?? 0;
              bObj.rotation.y = rot.y ?? 0;
              bObj.rotation.z = rot.z ?? 0;
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
  }, []);

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
          : "Impossible d'initialiser la démo. Essayez Chrome ou Safari récent."
      );
      setState("error");
    }
  }, [initThree, onPoseResults]);

  const stopDemo = useCallback(() => {
    try {
      cameraUtilRef.current?.stop?.();
    } catch {}
    try {
      poseRef.current?.close?.();
    } catch {}
    cameraUtilRef.current = null;
    poseRef.current = null;
    if (videoRef.current?.srcObject) {
      const tracks = (videoRef.current.srcObject as MediaStream).getTracks();
      tracks.forEach(t => t.stop());
      videoRef.current.srcObject = null;
    }
    setState("idle");
  }, []);

  useEffect(() => {
    return () => {
      stopDemo();
      if (rafRef.current) cancelAnimationFrame(rafRef.current);
      if (sceneRef.current) {
        sceneRef.current.cleanup();
        sceneRef.current = null;
      }
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
    <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
      <WebcamOverlay
        videoRef={videoRef}
        canvasRef={canvasRef}
        state={state}
        errorMsg={errorMsg}
        fitScore={fitScore}
        activeGarment={activeGarment}
        startDemo={startDemo}
        stopDemo={stopDemo}
      />
      <MannequinPreview
        threeHostRef={threeHostRef}
        biometrics={biometrics}
        activeGarment={activeGarment}
        setActiveGarment={setActiveGarment}
        garments={GARMENTS}
      />
    </div>
  );
}
