/// <reference types="vite/client" />

/** Variables expuestas en el cliente (prefijo VITE_). Evita errores TS en import.meta.env. */
interface ImportMetaEnv {
  readonly VITE_DISTRICT?: string;
  readonly VITE_DIVINEO_CHECKOUT_BASE?: string;
  readonly VITE_SHOP_VARIANT?: string;
  readonly VITE_INAUGURATION_STRIPE_CHECKOUT_URL?: string;
  readonly VITE_LAFAYETTE_STRIPE_CHECKOUT_URL?: string;
  readonly VITE_STRIPE_LINK_SOVEREIGNTY_4_5M?: string;
  readonly VITE_STRIPE_CHECKOUT_URL?: string;
  readonly VITE_STRIPE_LINK_SOVEREIGNTY_98K?: string;
  readonly VITE_MIRROR_DIGITAL_EVENT_URL?: string;
  readonly VITE_LICENSE_PAID?: string;
  readonly VITE_NINA_MESH_URL?: string;
  readonly VITE_FIREBASE_API_KEY?: string;
  readonly VITE_FIREBASE_AUTH_DOMAIN?: string;
  readonly VITE_FIREBASE_PROJECT_ID?: string;
  readonly VITE_FIREBASE_STORAGE_BUCKET?: string;
  readonly VITE_FIREBASE_MESSAGING_SENDER_ID?: string;
  readonly VITE_FIREBASE_APP_ID?: string;
  readonly VITE_FIREBASE_MEASUREMENT_ID?: string;
  readonly VITE_FIREBASE_APPCHECK_SITE_KEY?: string;
}
