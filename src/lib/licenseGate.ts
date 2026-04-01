/** Inyectado en build por `vite.config.ts` desde LICENSE_PAID / VITE_LICENSE_PAID. */

export function isSovereigntyLicenseActive(): boolean {
  const raw =
    typeof __TRYONYOU_LICENSE_PAID__ !== "undefined"
      ? __TRYONYOU_LICENSE_PAID__
      : "false";
  const v = String(raw).toLowerCase().trim();
  return v === "true" || v === "1" || v === "yes" || v === "on";
}
