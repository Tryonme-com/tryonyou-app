/**
 * Licencia soberana vía VITE_LICENSE_PAID (Vite solo expone variables VITE_* al cliente).
 */
export function isSovereigntyLicenseActive(): boolean {
  const raw = String(import.meta.env.VITE_LICENSE_PAID ?? "")
    .toLowerCase()
    .trim();
  if (!raw) return false;
  return raw === "true" || raw === "1" || raw === "yes" || raw === "on";
}
