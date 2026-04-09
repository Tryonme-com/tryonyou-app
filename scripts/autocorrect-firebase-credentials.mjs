/**
 * Autocorrige Firebase Web config desde el entorno sin exponer secretos por consola.
 *
 * Prioridad:
 * 1) VITE_FIREBASE_*
 * 2) FIREBASE_*
 * 3) valores existentes en firebase-applet-config.json
 *
 * Requisito de build: projectId fijo a gen-lang-client-0066102635.
 */
import { existsSync, readFileSync, writeFileSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const ROOT = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const APPLET_CONFIG_PATH = resolve(ROOT, "firebase-applet-config.json");
const FIREBASE_JS_PATH = resolve(ROOT, "src/lib/firebase.js");
const EXPECTED_PROJECT_ID = "gen-lang-client-0066102635";
const DOTENV_CANDIDATES = [
  resolve(ROOT, ".env"),
  resolve(ROOT, ".env.local"),
  resolve(ROOT, ".env.production"),
  resolve(ROOT, ".env.production.local"),
];

function sanitize(value) {
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

function pickEnv(...keys) {
  for (const k of keys) {
    const v = sanitize(process.env[k] ?? DOTENV_MAP.get(k) ?? "");
    if (v) return v;
  }
  return "";
}

function normalizeStorageBucket(raw, projectId) {
  let x = sanitize(raw);
  if (x.toLowerCase().startsWith("gs://")) {
    x = x.slice(5).trim();
  }
  const slash = x.indexOf("/");
  if (slash !== -1) x = x.slice(0, slash);
  if (!x && projectId) return `${projectId}.appspot.com`;
  return x;
}

function safeReadJson(path, fallback) {
  if (!existsSync(path)) return fallback;
  try {
    const parsed = JSON.parse(readFileSync(path, "utf8"));
    if (parsed && typeof parsed === "object") return parsed;
  } catch {
    // keep fallback
  }
  return fallback;
}

function parseDotenvFile(path) {
  if (!existsSync(path)) return new Map();
  const out = new Map();
  const raw = readFileSync(path, "utf8");
  for (const line of raw.split(/\r?\n/)) {
    const s = line.trim();
    if (!s || s.startsWith("#") || !s.includes("=")) continue;
    const idx = s.indexOf("=");
    const key = s.slice(0, idx).trim();
    if (!key) continue;
    const val = sanitize(s.slice(idx + 1));
    out.set(key, val);
  }
  return out;
}

const DOTENV_MAP = new Map();
for (const path of DOTENV_CANDIDATES) {
  const parsed = parseDotenvFile(path);
  for (const [k, v] of parsed.entries()) {
    if (!DOTENV_MAP.has(k) && v) DOTENV_MAP.set(k, v);
  }
}

function buildResolvedConfig(existing) {
  const injected = {
    apiKey: pickEnv("VITE_FIREBASE_API_KEY", "FIREBASE_API_KEY"),
    authDomain: pickEnv("VITE_FIREBASE_AUTH_DOMAIN", "FIREBASE_AUTH_DOMAIN"),
    messagingSenderId: pickEnv(
      "VITE_FIREBASE_MESSAGING_SENDER_ID",
      "FIREBASE_MESSAGING_SENDER_ID",
    ),
    appId: pickEnv("VITE_FIREBASE_APP_ID", "FIREBASE_APP_ID"),
    measurementId: pickEnv("VITE_FIREBASE_MEASUREMENT_ID", "FIREBASE_MEASUREMENT_ID"),
  };

  const projectId =
    pickEnv("VITE_FIREBASE_PROJECT_ID", "FIREBASE_PROJECT_ID") || EXPECTED_PROJECT_ID;

  const storageBucket = normalizeStorageBucket(
    pickEnv("VITE_FIREBASE_STORAGE_BUCKET", "FIREBASE_STORAGE_BUCKET") ||
      existing.storageBucket ||
      "",
    projectId,
  );

  return {
    _manifest:
      "TryOnYou Firebase Web — autocorrección desde entorno; projectId sellado para build/assert.",
    apiKey: injected.apiKey || sanitize(existing.apiKey),
    authDomain:
      injected.authDomain || sanitize(existing.authDomain) || `${projectId}.firebaseapp.com`,
    projectId: EXPECTED_PROJECT_ID,
    storageBucket: normalizeStorageBucket(storageBucket, EXPECTED_PROJECT_ID),
    messagingSenderId: injected.messagingSenderId || sanitize(existing.messagingSenderId),
    appId: injected.appId || sanitize(existing.appId),
    measurementId: injected.measurementId || sanitize(existing.measurementId),
  };
}

function writeFirebaseJs(config) {
  const injectedDefaults = {
    apiKey: sanitize(config.apiKey),
    authDomain: sanitize(config.authDomain),
    projectId: EXPECTED_PROJECT_ID,
    storageBucket: sanitize(config.storageBucket),
    messagingSenderId: sanitize(config.messagingSenderId),
    appId: sanitize(config.appId),
    measurementId: sanitize(config.measurementId),
  };

  const js = `/**
 * Firebase config bridge (legacy-compatible).
 * Se genera desde scripts/autocorrect-firebase-credentials.mjs
 */
import appletConfig from "../../firebase-applet-config.json";

const EXPECTED_PROJECT_ID = "${EXPECTED_PROJECT_ID}";
const INJECTED_DEFAULTS = ${JSON.stringify(injectedDefaults, null, 2)};

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
  if (!x && projectId) return \`\${projectId}.appspot.com\`;
  return x;
}

export function getFirebaseConfig() {
  const projectId = EXPECTED_PROJECT_ID;
  const apiKey = envValue("VITE_FIREBASE_API_KEY") || INJECTED_DEFAULTS.apiKey || clean(appletConfig.apiKey);
  const authDomain =
    envValue("VITE_FIREBASE_AUTH_DOMAIN") ||
    INJECTED_DEFAULTS.authDomain ||
    clean(appletConfig.authDomain) ||
    \`\${projectId}.firebaseapp.com\`;
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
`;

  writeFileSync(FIREBASE_JS_PATH, js, "utf8");
}

const current = safeReadJson(APPLET_CONFIG_PATH, {});
const resolved = buildResolvedConfig(current);
writeFileSync(APPLET_CONFIG_PATH, `${JSON.stringify(resolved, null, 2)}\n`, "utf8");
writeFirebaseJs(resolved);

const touched = [
  "apiKey",
  "authDomain",
  "projectId",
  "storageBucket",
  "messagingSenderId",
  "appId",
  "measurementId",
];
console.log(
  `[TryOnYou Firebase] autocorrección aplicada en ${APPLET_CONFIG_PATH} y ${FIREBASE_JS_PATH}. Campos: ${touched.join(", ")}`,
);
