/// <reference types="vite/client" />

interface ImportMetaEnv {
  // Firebase
  readonly VITE_FIREBASE_API_KEY: string;
  readonly VITE_FIREBASE_AUTH_DOMAIN: string;
  readonly VITE_FIREBASE_PROJECT_ID: string;
  readonly VITE_FIREBASE_STORAGE_BUCKET: string;
  readonly VITE_FIREBASE_MESSAGING_SENDER_ID: string;
  readonly VITE_FIREBASE_APP_ID: string;
  readonly VITE_FIREBASE_MEASUREMENT_ID: string;
  readonly VITE_FIREBASE_APPCHECK_SITE_KEY: string;
  // App
  readonly VITE_NINA_MESH_URL: string;
  readonly VITE_UI_ANIMATION: string;
  readonly VITE_PAU_MASTER_MODEL_URL: string;
  readonly VITE_STRIPE_CHECKOUT_API_ORIGIN: string;
  readonly VITE_INAUGURATION_STRIPE_CHECKOUT_URL: string;
  readonly VITE_LICENSE_PAID: string;
  readonly VITE_MIRROR_DIGITAL_EVENT_URL: string;
  readonly VITE_DISTRICT: string;
  readonly VITE_DIVINEO_CHECKOUT_BASE: string;
  readonly VITE_SHOP_VARIANT: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}

interface Window {
  __DIVINEO_CHECKOUT_BLOCKED__?: boolean;
  __DIVINEO_CHECKOUT_URL__?: string;
}
