import { type FirebaseApp, type FirebaseOptions, initializeApp } from "firebase/app";
import { getAnalytics, isSupported } from "firebase/analytics";
import { initializeAppCheck, ReCaptchaV3Provider } from "firebase/app-check";
import appletConfig from "../../firebase-applet-config.json";
import { viteFirebaseValue } from "./firebaseEnv";

let appSingleton: FirebaseApp | null = null;

function mergedOptions(): FirebaseOptions {
  const apiKey =
    viteFirebaseValue("VITE_FIREBASE_API_KEY") ||
    String(appletConfig.apiKey ?? "").trim() ||
    "";
  const authDomain =
    viteFirebaseValue("VITE_FIREBASE_AUTH_DOMAIN") || appletConfig.authDomain;
  const projectId =
    viteFirebaseValue("VITE_FIREBASE_PROJECT_ID") || appletConfig.projectId;
  const storageBucket =
    viteFirebaseValue("VITE_FIREBASE_STORAGE_BUCKET") ||
    appletConfig.storageBucket;
  const messagingSenderId =
    viteFirebaseValue("VITE_FIREBASE_MESSAGING_SENDER_ID") ||
    String(appletConfig.messagingSenderId ?? "").trim() ||
    "";
  const appId =
    viteFirebaseValue("VITE_FIREBASE_APP_ID") ||
    String(appletConfig.appId ?? "").trim() ||
    "";
  const mid =
    viteFirebaseValue("VITE_FIREBASE_MEASUREMENT_ID") ||
    String(appletConfig.measurementId ?? "").trim() ||
    "";
  return {
    apiKey,
    authDomain,
    projectId,
    storageBucket,
    messagingSenderId,
    appId,
    measurementId: mid || undefined,
  };
}

/**
 * Si `window.UserCheck` está autorizado, activa el flujo de depuración de App Check
 * antes de inicializar Firebase (evita bloqueos en entornos protegidos).
 */
export function applyUserCheckForAppCheck(): void {
  const w = window as Window & { UserCheck?: unknown };
  if (!w.UserCheck) return;
  const g = globalThis as unknown as {
    FIREBASE_APPCHECK_DEBUG_TOKEN?: boolean | string;
  };
  g.FIREBASE_APPCHECK_DEBUG_TOKEN = true;
}

export function initFirebaseApplet(): FirebaseApp | null {
  applyUserCheckForAppCheck();
  const opts = mergedOptions();
  if (!opts.apiKey || !opts.projectId) {
    console.warn(
      "[TryOnYou Firebase] Config incompleta: define VITE_FIREBASE_API_KEY (sin comillas en .env) o apiKey en firebase-applet-config.json. Proyecto esperado: gen-lang-client-0066102635.",
    );
    return null;
  }
  if (!appSingleton) {
    try {
      appSingleton = initializeApp(opts);
    } catch (e) {
      if (import.meta.env.DEV) {
        console.warn("[TryOnYou Firebase] init omitida (revisar apiKey / consola).", e);
      }
      return null;
    }
  }
  return appSingleton;
}

export async function initFirebaseAnalytics(app: FirebaseApp): Promise<void> {
  const mid = mergedOptions().measurementId;
  if (!mid) return;
  if (!(await isSupported())) return;
  getAnalytics(app);
}

export async function initFirebaseAppCheckIfConfigured(app: FirebaseApp): Promise<void> {
  const siteKey = viteFirebaseValue("VITE_FIREBASE_APPCHECK_SITE_KEY");
  const w = window as Window & { UserCheck?: unknown };
  if (w.UserCheck) return;
  if (!siteKey) return;
  initializeAppCheck(app, {
    provider: new ReCaptchaV3Provider(siteKey),
    isTokenAutoRefreshEnabled: true,
  });
}
