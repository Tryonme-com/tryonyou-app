/**
 * Lee variables Vite para Firebase sin comillas envolventes ni espacios accidentales
 * (causa típica de auth/invalid-api-key en .env).
 *
 * Patente PCT/EP2025/067317 — @CertezaAbsoluta @lo+erestu
 */

type ViteFirebaseKey =
  | "VITE_FIREBASE_API_KEY"
  | "VITE_FIREBASE_AUTH_DOMAIN"
  | "VITE_FIREBASE_PROJECT_ID"
  | "VITE_FIREBASE_STORAGE_BUCKET"
  | "VITE_FIREBASE_MESSAGING_SENDER_ID"
  | "VITE_FIREBASE_APP_ID"
  | "VITE_FIREBASE_MEASUREMENT_ID"
  | "VITE_FIREBASE_APPCHECK_SITE_KEY";

export function viteFirebaseValue(key: ViteFirebaseKey): string {
  const raw = import.meta.env[key];
  if (raw === undefined || raw === null) return "";
  let s = String(raw).trim();
  if (s.length >= 2) {
    const open = s[0];
    const close = s[s.length - 1];
    if (
      (open === '"' && close === '"') ||
      (open === "'" && close === "'")
    ) {
      s = s.slice(1, -1).trim();
    }
  }
  return s;
}
