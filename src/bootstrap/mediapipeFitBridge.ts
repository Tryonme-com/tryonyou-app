import { V9_IDENTITY_LABEL } from "../lib/privacyFirewall";

const SCRIPT_POSE = "https://cdn.jsdelivr.net/npm/@mediapipe/pose/pose.js";
const SCRIPT_CAMERA = "https://cdn.jsdelivr.net/npm/@mediapipe/camera_utils/camera_utils.js";
const DISPATCH_MIN_INTERVAL_MS = 120;
const FILTER_ALPHA = 0.22;

function emitFitLabel(label: string): void {
  window.dispatchEvent(
    new CustomEvent<{ label: string }>("tryonyou:fit", {
      detail: { label },
    }),
  );
}

function dist2(a: PoseLandmark, b: PoseLandmark): number {
  return Math.hypot(a.x - b.x, a.y - b.y);
}

function computeElasticityRatio(landmarks: PoseLandmark[]): number {
  if (!landmarks || landmarks.length < 25) return 0.5;
  const shoulder = dist2(landmarks[11], landmarks[12]);
  const hip = dist2(landmarks[23], landmarks[24]);
  return shoulder / Math.max(hip, 1e-6);
}

function verdictToUiLabel(verdict: "aligned" | "drape_bias" | "tension_bias"): string {
  if (verdict === "aligned") return "Cohérence drape — tenue";
  if (verdict === "drape_bias") return "Préférence drapé";
  return "Préférence tenue";
}

function fabricFitComparator(elasticityEma: number, band: [number, number] = [0.82, 1.18]) {
  if (elasticityEma >= band[0] && elasticityEma <= band[1]) return "aligned" as const;
  if (elasticityEma < band[0]) return "drape_bias" as const;
  return "tension_bias" as const;
}

function ensureScript(src: string): Promise<void> {
  return new Promise((resolve, reject) => {
    const existing = document.querySelector<HTMLScriptElement>(`script[data-mediapipe-src="${src}"]`);
    if (existing) {
      if (existing.dataset.loaded === "1") {
        resolve();
        return;
      }
      existing.addEventListener("load", () => resolve(), { once: true });
      existing.addEventListener("error", () => reject(new Error(`No se pudo cargar ${src}`)), {
        once: true,
      });
      return;
    }
    const script = document.createElement("script");
    script.src = src;
    script.async = true;
    script.crossOrigin = "anonymous";
    script.dataset.mediapipeSrc = src;
    script.addEventListener("load", () => {
      script.dataset.loaded = "1";
      resolve();
    });
    script.addEventListener("error", () => reject(new Error(`No se pudo cargar ${src}`)));
    document.head.appendChild(script);
  });
}

function ensureHiddenMediaContainer(): {
  container: HTMLDivElement;
  video: HTMLVideoElement;
  canvas: HTMLCanvasElement;
  remove: () => void;
} {
  const existing = document.getElementById("tryonyou-mediapipe-bridge");
  if (existing) existing.remove();

  const container = document.createElement("div");
  container.id = "tryonyou-mediapipe-bridge";
  container.style.position = "fixed";
  container.style.width = "1px";
  container.style.height = "1px";
  container.style.opacity = "0";
  container.style.pointerEvents = "none";
  container.style.inset = "0";
  container.style.zIndex = "-1";

  const video = document.createElement("video");
  video.id = "tryonyou-input-video";
  video.playsInline = true;
  video.muted = true;

  const canvas = document.createElement("canvas");
  canvas.id = "tryonyou-output-canvas";

  container.appendChild(video);
  container.appendChild(canvas);
  document.body.appendChild(container);

  return {
    container,
    video,
    canvas,
    remove: () => container.remove(),
  };
}

async function hasVideoInput(): Promise<boolean> {
  if (!navigator.mediaDevices || typeof navigator.mediaDevices.enumerateDevices !== "function") {
    return false;
  }
  try {
    const devices = await navigator.mediaDevices.enumerateDevices();
    return devices.some((device) => device.kind === "videoinput");
  } catch {
    return false;
  }
}

type BridgeCleanup = () => void;

export async function startMediapipeFitBridge(): Promise<BridgeCleanup> {
  if (typeof window === "undefined" || typeof document === "undefined") {
    return () => undefined;
  }

  let cameraInstance: MediaPipeCamera | null = null;
  let stopped = false;
  let rafId = 0;
  let pendingLabel = "";
  let lastDispatchAt = 0;
  let scheduleRequested = false;

  const media = ensureHiddenMediaContainer();
  const canvasCtx = media.canvas.getContext("2d");
  if (!canvasCtx) {
    emitFitLabel(V9_IDENTITY_LABEL);
    return () => media.remove();
  }

  const scheduleDispatch = () => {
    if (scheduleRequested) return;
    scheduleRequested = true;
    rafId = window.requestAnimationFrame(() => {
      scheduleRequested = false;
      if (stopped || !pendingLabel) return;
      const now = performance.now();
      if (now - lastDispatchAt < DISPATCH_MIN_INTERVAL_MS) {
        scheduleDispatch();
        return;
      }
      lastDispatchAt = now;
      emitFitLabel(pendingLabel);
    });
  };

  try {
    await ensureScript(SCRIPT_POSE);
    await ensureScript(SCRIPT_CAMERA);
  } catch {
    emitFitLabel(V9_IDENTITY_LABEL);
    return () => {
      stopped = true;
      if (rafId) window.cancelAnimationFrame(rafId);
      media.remove();
    };
  }

  const PoseCtor = window.Pose;
  const CameraCtor = window.Camera;
  if (!PoseCtor || !CameraCtor) {
    emitFitLabel(V9_IDENTITY_LABEL);
    return () => {
      stopped = true;
      if (rafId) window.cancelAnimationFrame(rafId);
      media.remove();
    };
  }

  let ema = 0.5;

  const resizeCanvas = () => {
    media.canvas.width = Math.max(window.innerWidth, 1);
    media.canvas.height = Math.max(window.innerHeight, 1);
  };
  resizeCanvas();
  window.addEventListener("resize", resizeCanvas);

  const pose = new PoseCtor({
    locateFile: (file: string) => `https://cdn.jsdelivr.net/npm/@mediapipe/pose/${file}`,
  });
  pose.setOptions({
    modelComplexity: 1,
    smoothLandmarks: true,
    minDetectionConfidence: 0.5,
  });

  pose.onResults((results) => {
    if (stopped) return;
    const width = media.canvas.width;
    const height = media.canvas.height;
    canvasCtx.save();
    canvasCtx.clearRect(0, 0, width, height);
    if (results.image) {
      canvasCtx.drawImage(results.image, 0, 0, width, height);
    }
    const landmarks = results.poseLandmarks;
    if (landmarks && landmarks.length >= 33) {
      const ratio = computeElasticityRatio(landmarks);
      ema = FILTER_ALPHA * ratio + (1 - FILTER_ALPHA) * ema;
      const verdict = fabricFitComparator(ema);
      pendingLabel = verdictToUiLabel(verdict);
      scheduleDispatch();
    }
    canvasCtx.restore();
  });

  const available = await hasVideoInput();
  if (!available) {
    emitFitLabel(V9_IDENTITY_LABEL);
    return () => {
      stopped = true;
      if (rafId) window.cancelAnimationFrame(rafId);
      window.removeEventListener("resize", resizeCanvas);
      media.remove();
    };
  }

  cameraInstance = new CameraCtor(media.video, {
    onFrame: async () => {
      if (stopped) return;
      await pose.send({ image: media.video });
    },
    width: 1280,
    height: 720,
  });

  try {
    await cameraInstance.start();
  } catch {
    emitFitLabel(V9_IDENTITY_LABEL);
  }

  return () => {
    stopped = true;
    if (rafId) window.cancelAnimationFrame(rafId);
    window.removeEventListener("resize", resizeCanvas);
    cameraInstance?.stop?.();
    media.remove();
  };
}
