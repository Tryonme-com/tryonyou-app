/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_FIREBASE_API_KEY: string;
  readonly VITE_FIREBASE_AUTH_DOMAIN: string;
  readonly VITE_FIREBASE_PROJECT_ID: string;
  readonly VITE_FIREBASE_STORAGE_BUCKET: string;
  readonly VITE_FIREBASE_MESSAGING_SENDER_ID: string;
  readonly VITE_FIREBASE_APP_ID: string;
  readonly VITE_FIREBASE_MEASUREMENT_ID: string;
  readonly VITE_NINA_MESH_URL: string;
  readonly VITE_SHOP_VARIANT: string;
  readonly VITE_DIVINEO_CHECKOUT_BASE: string;
  readonly VITE_STRIPE_PUBLISHABLE_KEY: string;
  readonly VITE_STRIPE_CHECKOUT_URL?: string;
  readonly VITE_INAUGURATION_STRIPE_CHECKOUT_URL?: string;
  readonly VITE_STRIPE_LINK_SOVEREIGNTY_4_5M?: string;
  readonly VITE_STRIPE_LINK_SOVEREIGNTY_98K?: string;
  readonly VITE_LICENSE_KEY: string;
  readonly VITE_PUBLIC_DOMAIN: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}

declare global {
  interface Window {
    __DIVINEO_CHECKOUT_URL__: string;
    __DIVINEO_CHECKOUT_BLOCKED__?: boolean;
    __TRYONYOU_LAST_FLOW_TOKEN__?: string;
    empireFinalProtocol?: {
      bootstrapEmpireFinalProtocol: () => void;
      executePauSnap: (input?: { trigger?: string }) => Promise<{
        flowToken: string;
        anthraciteSeal: boolean;
      }>;
      markSouverainetePaid: (input?: {
        source?: string;
        flowToken?: string;
        sessionId?: string;
      }) => void;
      hydrateSouveraineteFromUrl: () => void;
      resolveStripeHref: (fallbackHref?: string) => string;
      registerPaymentIntent: (input: {
        flowToken?: string;
        checkoutUrl?: string;
        buttonId?: string;
        source?: string;
      }) => Promise<void>;
      registerPaymentSuccess: (input: {
        flowToken?: string;
        sessionId?: string;
      }) => Promise<void>;
    };
  }
}

export {};
