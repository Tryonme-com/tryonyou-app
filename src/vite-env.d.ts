/// <reference types="vite/client" />

interface Window {
  __DIVINEO_CHECKOUT_URL__?: string;
  __TRYONYOU_MIRROR_DIGITAL_PATH__?: string;
  __TRYONYOU_POSTAL__?: string;
  UserCheck?: unknown;
  empireFinalProtocol?: {
    resolveStripeHref?: (current: string) => string;
    executePauSnap?: (payload: { trigger: string }) => Promise<{ flowToken?: string } | undefined>;
    registerPaymentIntent?: (payload: {
      flowToken: string;
      checkoutUrl: string;
      buttonId: string;
      source: string;
    }) => Promise<unknown>;
  };
}
