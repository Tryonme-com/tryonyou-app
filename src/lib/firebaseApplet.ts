import { type FirebaseApp, type FirebaseOptions, initializeApp } from "firebase/app";
import { getAnalytics, isSupported } from "firebase/analytics";
import { initializeAppCheck, ReCaptchaV3Provider } from "firebase/app-check";
import appletConfig from "../../firebase-applet-config.json";

let appSingleton: FirebaseApp | null = null;

function mergedOptions(): FirebaseOptions {
  const env = import.meta.env;
  return {
    apiKey: env.VITE_FIREBASE_API_KEY || appletConfig.apiKey || "",
    authDomain: appletConfig.authDomain,
    projectId: appletConfig.projectId,
    storageBucket: appletConfig.storageBucket,
    messagingSenderId:
      env.VITE_FIREBASE_MESSAGING_SENDER_ID || appletConfig.messagingSenderId || "",
    appId: env.VITE_FIREBASE_APP_ID || appletConfig.appId || "",
    measurementId:
      env.VITE_FIREBASE_MEASUREMENT_ID || appletConfig.measurementId || undefined,
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
      "[TryOnYou Firebase] Config incompleta: rellena firebase-applet-config.json o VITE_FIREBASE_*",
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
  const siteKey = import.meta.env.VITE_FIREBASE_APPCHECK_SITE_KEY;
  const w = window as Window & { UserCheck?: unknown };
  if (w.UserCheck) return;
  if (!siteKey?.trim()) return;
  initializeAppCheck(app, {
    provider: new ReCaptchaV3Provider(siteKey),
    isTokenAutoRefreshEnabled: true,
  });
}
