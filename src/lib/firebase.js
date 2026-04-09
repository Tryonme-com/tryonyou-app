/**
 * Firebase config bridge (legacy-compatible).
 * Se genera desde scripts/autocorrect-firebase-credentials.mjs
 */
import appletConfig from "../../firebase-applet-config.json";

const EXPECTED_PROJECT_ID = "gen-lang-client-0066102635";
const INJECTED_DEFAULTS = {
  "apiKey": "",
  "authDomain": "gen-lang-client-0066102635.firebaseapp.com",
  "projectId": "gen-lang-client-0066102635",
  "storageBucket": "gen-lang-client-0066102635.appspot.com",
  "messagingSenderId": "8800075004",
  "appId": "1:8800075004:web:diamond",
  "measurementId": ""
};

function clean(value) {
  if (value === undefined || value === null) return "";
  let s = String(value).trim();
  if (s.length >= 2) {
    const open = s[0];
    const close = s[s.length - 1];
    if ((open === '"' && close === '"') || (open === "'" && close === "'")) {
      s = s.slice(1, -1).trim();
    }
  }
  return s;
}

function envValue(key) {
  return clean(import.meta.env?.[key]);
}

function normalizeStorageBucket(raw, projectId) {
  let x = clean(raw);
  if (x.toLowerCase().startsWith("gs://")) x = x.slice(5).trim();
  const slash = x.indexOf("/");
  if (slash !== -1) x = x.slice(0, slash);
  if (!x && projectId) return `${projectId}.appspot.com`;
  return x;
}

export function getFirebaseConfig() {
  const projectId = EXPECTED_PROJECT_ID;
  const apiKey = envValue("VITE_FIREBASE_API_KEY") || INJECTED_DEFAULTS.apiKey || clean(appletConfig.apiKey);
  const authDomain =
    envValue("VITE_FIREBASE_AUTH_DOMAIN") ||
    INJECTED_DEFAULTS.authDomain ||
    clean(appletConfig.authDomain) ||
    `${projectId}.firebaseapp.com`;
  const messagingSenderId =
    envValue("VITE_FIREBASE_MESSAGING_SENDER_ID") ||
    INJECTED_DEFAULTS.messagingSenderId ||
    clean(appletConfig.messagingSenderId);
  const appId = envValue("VITE_FIREBASE_APP_ID") || INJECTED_DEFAULTS.appId || clean(appletConfig.appId);
  const measurementId =
    envValue("VITE_FIREBASE_MEASUREMENT_ID") ||
    INJECTED_DEFAULTS.measurementId ||
    clean(appletConfig.measurementId);
  const storageBucket = normalizeStorageBucket(
    envValue("VITE_FIREBASE_STORAGE_BUCKET") ||
      INJECTED_DEFAULTS.storageBucket ||
      clean(appletConfig.storageBucket),
    projectId,
  );
  return {
    apiKey,
    authDomain,
    projectId,
    storageBucket,
    messagingSenderId,
    appId,
    measurementId: measurementId || undefined,
  };
}

const firebaseConfig = getFirebaseConfig();
export default firebaseConfig;
