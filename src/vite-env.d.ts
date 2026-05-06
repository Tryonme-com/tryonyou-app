/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_DIVINEO_CHECKOUT_BASE?: string;
  readonly VITE_FIREBASE_API_KEY?: string;
  readonly VITE_FIREBASE_APP_ID?: string;
  readonly VITE_FIREBASE_APPCHECK_SITE_KEY?: string;
  readonly VITE_FIREBASE_AUTH_DOMAIN?: string;
  readonly VITE_FIREBASE_MEASUREMENT_ID?: string;
  readonly VITE_FIREBASE_MESSAGING_SENDER_ID?: string;
  readonly VITE_FIREBASE_PROJECT_ID?: string;
  readonly VITE_FIREBASE_STORAGE_BUCKET?: string;
  readonly VITE_GOOGLE_API_KEY?: string;
  readonly VITE_INAUGURATION_STRIPE_CHECKOUT_URL?: string;
  readonly VITE_LAFAYETTE_STRIPE_CHECKOUT_URL?: string;
  readonly VITE_NINA_MESH_URL?: string;
  readonly VITE_SHOP_DOMAIN?: string;
  readonly VITE_SHOP_VARIANT?: string;
  readonly VITE_STRIPE_PUBLIC_KEY?: string;
  readonly VITE_STRIPE_PUBLIC_KEY_FR?: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}

interface Window {
  __DIVINEO_CHECKOUT_BLOCKED__?: boolean;
  __DIVINEO_CHECKOUT_URL__?: string;
}
