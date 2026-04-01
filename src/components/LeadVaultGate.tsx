import type { ReactNode } from "react";
import { isSovereigntyLicenseActive } from "../lib/licenseGate";

/**
 * No renderiza hijos si la licencia soberana no está activa (datos leads / CRM en UI).
 */
export function LeadVaultGate({ children }: { children: ReactNode }) {
  if (!isSovereigntyLicenseActive()) {
    return null;
  }
  return <>{children}</>;
}
