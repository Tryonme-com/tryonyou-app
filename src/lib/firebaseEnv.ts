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

/** Quita BOM, anchura cero y espacios unicode que suelen colarse en .env / Vercel. */
function stripInvisibleAndEdgeSpaces(s: string): string {
  return s
    .replace(/\uFEFF/g, "")
    .replace(/[\u200B-\u200D\u2060]/g, "")
    .replace(/[\u00A0\u1680\u2000-\u200A\u202F\u205F\u3000]/g, "")
    .trim();
}

/**
 * Firebase `storageBucket` debe ser solo `proyecto.appspot.com` (sin `gs://` ni path).
 * Un `.env` con `gs://bucket/path` provoca mismatch con Storage y errores de acceso.
 * Si no queda valor válido, devuelve `undefined` (contrato Firebase: string | undefined, no "").
 */
export function normalizeFirebaseStorageBucket(raw: string): string | undefined {
  let x = stripInvisibleAndEdgeSpaces(String(raw ?? ""));
  if (x.length >= 2) {
    const open = x[0];
    const close = x[x.length - 1];
    if (
      (open === '"' && close === '"') ||
      (open === "'" && close === "'")
    ) {
      x = stripInvisibleAndEdgeSpaces(x.slice(1, -1));
    }
  }
  const lower = x.toLowerCase();
  if (lower.startsWith("gs://")) {
    x = stripInvisibleAndEdgeSpaces(x.slice(5));
  }
  const slash = x.indexOf("/");
  if (slash !== -1) {
    x = x.slice(0, slash);
  }
  const out = stripInvisibleAndEdgeSpaces(x);
  return out || undefined;
}
