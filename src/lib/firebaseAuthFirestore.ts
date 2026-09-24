/**
 * Auth + Firestore sobre la misma app que `initFirebaseApplet()` (VITE_FIREBASE_* + firebase-applet-config.json).
 *
 * Sustituye el patrón manual `initializeApp(firebaseConfig)` sin duplicar IDs en código: la `apiKey` solo por env.
 * authDomain, projectId y storageBucket deben pertenecer al **mismo** proyecto Firebase (evita mezclar dominios).
 *
 * Patente PCT/EP2025/067317 — @CertezaAbsoluta @lo+erestu
 * Bajo Protocolo de Soberanía V10 - Founder: Rubén
 */
import { getAuth, type Auth } from "firebase/auth";
import { getFirestore, type Firestore } from "firebase/firestore";
import { initFirebaseApplet } from "./firebaseApplet";

const app = initFirebaseApplet();

/** `null` si la config no está completa (revisa consola y `.env`). */
export const auth: Auth | null = app ? getAuth(app) : null;

/** `null` si la config no está completa. */
export const db: Firestore | null = app ? getFirestore(app) : null;
