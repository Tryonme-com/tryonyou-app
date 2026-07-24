/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly DEV: boolean;
  readonly MODE: string;
  readonly PROD: boolean;
  readonly BASE_URL: string;
  readonly VITE_DISTRICT?: string;
  readonly VITE_DIVINEO_CHECKOUT_BASE?: string;
  readonly VITE_SHOP_VARIANT?: string;
  readonly VITE_PAU_MASTER_MODEL_URL?: string;
  readonly VITE_FIREBASE_API_KEY?: string;
  readonly VITE_FIREBASE_AUTH_DOMAIN?: string;
  readonly VITE_FIREBASE_PROJECT_ID?: string;
  readonly VITE_FIREBASE_STORAGE_BUCKET?: string;
  readonly VITE_FIREBASE_MESSAGING_SENDER_ID?: string;
  readonly VITE_FIREBASE_APP_ID?: string;
  readonly VITE_FIREBASE_MEASUREMENT_ID?: string;
  readonly VITE_FIREBASE_APPCHECK_SITE_KEY?: string;
  readonly VITE_FIREBASE_APPCHECK_DEBUG?: string;
  readonly VITE_FIREBASE_APPCHECK_BYPASS?: string;
  readonly VITE_SHOPIFY_PERFECT_CHECKOUT_URL?: string;
  readonly VITE_SHOPIFY_STORE_DOMAIN?: string;
  readonly VITE_SHOPIFY_VARIANT_ID?: string;
  readonly VITE_MIRROR_DIGITAL_PATH?: string;
  readonly VITE_STRIPE_PUBLIC_KEY_FR?: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}

type UserCheckContext = {
  isAuthorized?: boolean;
  role?: string;
  account_scope?: string;
  accountEnvironment?: string;
  contract?: string;
  location?: string;
  [key: string]: unknown;
};

type MediaPipePose = {
  setOptions: (options: Record<string, unknown>) => void;
  onResults: (cb: (results: PoseResults) => void) => void;
  send: (payload: { image: HTMLVideoElement }) => Promise<void>;
};

type MediaPipePoseCtor = new (opts: { locateFile: (file: string) => string }) => MediaPipePose;

type MediaPipeCamera = {
  start: () => Promise<void>;
  stop?: () => void;
};

type MediaPipeCameraCtor = new (
  video: HTMLVideoElement,
  opts: {
    onFrame: () => Promise<void>;
    width: number;
    height: number;
  },
) => MediaPipeCamera;

type PoseLandmark = {
  x: number;
  y: number;
  z?: number;
  visibility?: number;
};

type PoseResults = {
  image?: HTMLImageElement | HTMLCanvasElement | HTMLVideoElement | ImageBitmap;
  poseLandmarks?: PoseLandmark[];
};

interface Window {
  __DIVINEO_CHECKOUT_URL__?: string;
  __TRYONYOU_OPERATIONAL_STATE__?: string;
  __TRYONYOU_POSTAL__?: string;
  __TRYONYOU_MIRROR_DIGITAL_PATH__?: string;
  UserCheck?: UserCheckContext;
  Pose?: MediaPipePoseCtor;
  Camera?: MediaPipeCameraCtor;
  POSE_CONNECTIONS?: Array<[number, number]>;
}
