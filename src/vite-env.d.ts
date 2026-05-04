/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_API_BASE_URL?: string;
  readonly VITE_APP_ENV?: string;
  readonly VITE_DIVINEO_CHECKOUT_BASE?: string;
  readonly VITE_FIREBASE_API_KEY?: string;
  readonly VITE_FIREBASE_APP_ID?: string;
  readonly VITE_FIREBASE_AUTH_DOMAIN?: string;
  readonly VITE_FIREBASE_MEASUREMENT_ID?: string;
  readonly VITE_FIREBASE_MESSAGING_SENDER_ID?: string;
  readonly VITE_FIREBASE_PROJECT_ID?: string;
  readonly VITE_FIREBASE_STORAGE_BUCKET?: string;
  readonly VITE_LAFAYETTE_CHECKOUT_URL?: string;
  readonly VITE_LICENSE_GATE_ENABLED?: string;
  readonly VITE_MIRROR_DIGITAL_ENDPOINT?: string;
  readonly VITE_NINA_MESH_URL?: string;
  readonly VITE_PAU_ANIMATIONS_VERBOSE?: string;
  readonly VITE_SHOP_VARIANT?: string;
  readonly VITE_STRIPE_PRICE_ID_FR?: string;
  readonly VITE_STRIPE_PUBLIC_KEY_FR?: string;
  readonly VITE_TRYONYOU_API_URL?: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}

interface Window {
  __DIVINEO_CHECKOUT_BLOCKED__?: boolean;
  __DIVINEO_CHECKOUT_URL__?: string;
}
