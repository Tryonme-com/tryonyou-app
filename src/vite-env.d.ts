/// <reference types="vite/client" />

interface ImportMetaEnv {
  /** Todas las claves VITE_* se tipan como string; ausencia en runtime → undefined. */
  readonly VITE_DISTRICT: string | undefined;
  readonly VITE_CONTRACT_VALUE: string | undefined;
  readonly VITE_LICENSE_PAID: string | undefined;
  readonly VITE_FIREBASE_API_KEY: string | undefined;
  readonly VITE_FIREBASE_MESSAGING_SENDER_ID: string | undefined;
  readonly VITE_FIREBASE_APP_ID: string | undefined;
  readonly VITE_FIREBASE_MEASUREMENT_ID: string | undefined;
  readonly VITE_FIREBASE_APPCHECK_SITE_KEY: string | undefined;
  readonly VITE_DIVINEO_CHECKOUT_BASE: string | undefined;
  readonly VITE_SHOP_VARIANT: string | undefined;
  readonly VITE_NINA_MESH_URL: string | undefined;
  readonly VITE_LAFAYETTE_STRIPE_CHECKOUT_URL: string | undefined;
  readonly VITE_STRIPE_LINK_SOVEREIGNTY_4_5M: string | undefined;
  readonly VITE_STRIPE_LINK_SOVEREIGNTY_98K: string | undefined;
  readonly VITE_STRIPE_CHECKOUT_URL: string | undefined;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}

interface Window {
  __DIVINEO_CHECKOUT_URL__?: string;
}
