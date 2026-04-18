import {
  createContext,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from "react";
import { getInaugurationStripeCheckoutUrl } from "../lib/lafayetteCheckout";
import { fetchParisInaugurationCheckoutUrl } from "../services/paymentService";

export type ParisStripeCheckoutContextValue = {
  /** Hay enlace estático en env o la API devolvió URL de sesión (probe inicial). */
  checkoutApiReady: boolean;
  checkoutProbeError: string | null;
};

const ParisStripeCheckoutContext = createContext<ParisStripeCheckoutContextValue | null>(
  null,
);

export function ParisStripeCheckoutProvider({ children }: { children: ReactNode }) {
  const [checkoutApiReady, setCheckoutApiReady] = useState(false);
  const [checkoutProbeError, setCheckoutProbeError] = useState<string | null>(null);

  useEffect(() => {
    const staticUrl = getInaugurationStripeCheckoutUrl().trim();
    if (staticUrl) {
      setCheckoutApiReady(true);
      return;
    }
    let cancelled = false;
    void (async () => {
      const url = await fetchParisInaugurationCheckoutUrl();
      if (cancelled) return;
      if (url) {
        setCheckoutApiReady(true);
      } else {
        setCheckoutProbeError("stripe_checkout_probe_failed");
      }
    })();
    return () => {
      cancelled = true;
    };
  }, []);

  const value = useMemo(
    () => ({ checkoutApiReady, checkoutProbeError }),
    [checkoutApiReady, checkoutProbeError],
  );

  return (
    <ParisStripeCheckoutContext.Provider value={value}>
      {children}
    </ParisStripeCheckoutContext.Provider>
  );
}

/** Sin Provider, no bloquea el UI (compatibilidad con rutas legacy). */
export function useParisStripeCheckout(): ParisStripeCheckoutContextValue {
  const v = useContext(ParisStripeCheckoutContext);
  if (!v) {
    return { checkoutApiReady: true, checkoutProbeError: null };
  }
  return v;
}
