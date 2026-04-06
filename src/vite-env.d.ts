/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_STRIPE_LAFAYETTE_CHECKOUT_URL?: string;
  readonly VITE_STRIPE_LINK_SOVEREIGNTY_4_5M?: string;
  readonly VITE_FIREBASE_API_KEY?: string;
  readonly VITE_FIREBASE_MESSAGING_SENDER_ID?: string;
  readonly VITE_FIREBASE_APP_ID?: string;
  readonly VITE_FIREBASE_MEASUREMENT_ID?: string;
  readonly VITE_FIREBASE_APPCHECK_SITE_KEY?: string;
  readonly VITE_DISTRICT?: string;
  readonly VITE_DIVINEO_CHECKOUT_BASE?: string;
  readonly VITE_SHOP_VARIANT?: string;
  readonly VITE_NINA_MESH_URL?: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}
