/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly DEV: boolean;
  readonly VITE_DISTRICT?: string;
  readonly VITE_DIVINEO_CHECKOUT_BASE?: string;
  readonly VITE_FIREBASE_API_KEY?: string;
  readonly VITE_FIREBASE_AUTH_DOMAIN?: string;
  readonly VITE_FIREBASE_PROJECT_ID?: string;
  readonly VITE_FIREBASE_STORAGE_BUCKET?: string;
  readonly VITE_FIREBASE_MESSAGING_SENDER_ID?: string;
  readonly VITE_FIREBASE_APP_ID?: string;
  readonly VITE_FIREBASE_MEASUREMENT_ID?: string;
  readonly VITE_FIREBASE_APPCHECK_SITE_KEY?: string;
  readonly VITE_PAU_MASTER_MODEL_URL?: string;
  readonly VITE_SHOP_VARIANT?: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}

type TryOnYouUserCheck = {
  isAuthorized?: boolean;
  location?: string;
  postal?: string;
  postalCode?: string;
  role?: string;
  nodos?: string[];
};

interface Window {
  UserCheck?: TryOnYouUserCheck | unknown;
  __DIVINEO_CHECKOUT_BLOCKED__?: boolean;
  __DIVINEO_CHECKOUT_URL__?: string;
  __TRYONYOU_LAST_FLOW_TOKEN__?: string;
  __TRYONYOU_MIRROR_DIGITAL_PATH__?: string;
  __TRYONYOU_OPERATIONAL_STATE__?: string;
  __TRYONYOU_POSTAL__?: string;
  empireFinalProtocol?: {
    executePauSnap?: (payload: Record<string, unknown>) => Promise<{ flowToken?: string }>;
    registerPaymentIntent?: (payload: Record<string, unknown>) => Promise<unknown>;
    resolveStripeHref?: (href: string) => string;
  };
}
