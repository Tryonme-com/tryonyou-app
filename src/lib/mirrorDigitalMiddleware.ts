/**
 * Capa intermedia: cada clic relevante dispara primero el POST al proxy Make (api/index.py).
 * Meta solo con datos de runtime (sin placeholders comerciales).
 */

import { postMirrorDigitalEvent } from "./mirrorDigitalClient";

function runtimeMeta(): Record<string, string> {
  if (typeof window === "undefined") return {};
  const m: Record<string, string> = { pathname: window.location.pathname };
  const q = window.location.search;
  if (q) m.search = q;
  return m;
}

export const mirrorDigitalMiddleware = {
  onBalmainClick(elasticLabel: string): void {
    void postMirrorDigitalEvent("balmain_click", {
      elastic_label: elasticLabel,
      ...runtimeMeta(),
    });
  },

  onReserveFittingClick(elasticLabel: string): void {
    void postMirrorDigitalEvent("reserve_fitting_click", {
      intent: "reserve",
      elastic_label: elasticLabel,
      ...runtimeMeta(),
    });
  },
} as const;
