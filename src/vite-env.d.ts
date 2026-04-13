/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_DISTRICT?: string;
  readonly VITE_STRIPE_CHECKOUT_API_ORIGIN?: string;
  readonly VITE_STRIPE_PUBLIC_KEY_FR?: string;
  readonly VITE_STRIPE_PUBLIC_KEY?: string;
  readonly VITE_INAUGURATION_STRIPE_CHECKOUT_URL?: string;
  readonly VITE_LAFAYETTE_STRIPE_CHECKOUT_URL?: string;
  readonly VITE_DIVINEO_CHECKOUT_BASE?: string;
  readonly VITE_SHOP_VARIANT?: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}
