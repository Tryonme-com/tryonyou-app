/**
 * RobertEngine — Motor Holístico MediaPipe para certeza biométrica Zero-Size.
 * Inicializa el pipeline de seguimiento corporal completo (pose + manos + cara).
 * Ref: PCT/EP2025/067317 | TRYONYOU V10 OMEGA
 */

type Landmark = { x: number; y: number; z: number; visibility?: number };

type HolisticResults = {
  poseLandmarks?: Landmark[];
  leftHandLandmarks?: Landmark[];
  rightHandLandmarks?: Landmark[];
  faceLandmarks?: Landmark[];
};

type HolisticInstance = {
  setOptions: (opts: Record<string, unknown>) => void;
  onResults: (cb: (results: HolisticResults) => void) => void;
  send: (data: { image: HTMLVideoElement }) => Promise<void>;
};

declare global {
  interface Window {
    Holistic?: new (options: { locateFile: (file: string) => string }) => HolisticInstance;
    Camera?: new (
      element: HTMLVideoElement,
      options: {
        onFrame: () => void | Promise<void>;
        width: number;
        height: number;
      },
    ) => { start: () => Promise<void> };
  }
}

const HOLISTIC_CDN = "https://cdn.jsdelivr.net/npm/@mediapipe/holistic/";

export function initializeHolisticEngine(): void {
  const video = document.getElementById("input_video") as HTMLVideoElement | null;
  const canvas = document.getElementById("output_canvas") as HTMLCanvasElement | null;

  if (!video || !canvas) {
    console.warn("RobertEngine: elementos DOM (input_video / output_canvas) no encontrados.");
    return;
  }

  const HolisticCtor = window.Holistic;
  const CameraCtor = window.Camera;

  if (!HolisticCtor || !CameraCtor) {
    console.warn("RobertEngine: MediaPipe Holistic no cargado (CDN pendiente).");
    return;
  }

  const ctx = canvas.getContext("2d");

  const holistic = new HolisticCtor({
    locateFile: (file: string) => `${HOLISTIC_CDN}${file}`,
  });

  holistic.setOptions({
    modelComplexity: 1,
    smoothLandmarks: true,
    minDetectionConfidence: 0.5,
    minTrackingConfidence: 0.5,
  });

  holistic.onResults((results: HolisticResults) => {
    if (!ctx) return;
    const w = canvas.width;
    const h = canvas.height;
    ctx.save();
    ctx.clearRect(0, 0, w, h);
    if (results.poseLandmarks && results.poseLandmarks.length > 0) {
      window.dispatchEvent(
        new CustomEvent("tryonyou:holistic_ready", { detail: results }),
      );
    }
    ctx.restore();
  });

  const camera = new CameraCtor(video, {
    onFrame: async () => {
      await holistic.send({ image: video });
    },
    width: 1280,
    height: 720,
  });

  camera.start().catch((err: unknown) => {
    console.warn("RobertEngine: cámara no iniciada —", err);
  });
}
