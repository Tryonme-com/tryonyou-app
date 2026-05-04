/**
 * 🛡️ EXTRACCIÓN DE BIOMETRÍA - TRYONYOU1
 * Criba de datos para proyección Robert Engine
 *
 * Patente PCT/EP2025/067317 — @CertezaAbsoluta @lo+erestu
 * Bajo Protocolo de Soberanía V10 - Founder: Rubén
 */
import { getStorage, ref, getDownloadURL } from "firebase/storage";
import {
  loadNinaMeshFromResponseStream,
  meshUrlFromEnv,
} from "../divineo/loadNinaMeshStream";
import { initFirebaseApplet } from "./firebaseApplet";

const SOVEREIGN_MESH_STORAGE_PATH = "biometria/nina_perfecta_mesh.json";

async function resolveSovereignMeshUrl(): Promise<string | null> {
  const envUrl = meshUrlFromEnv();
  if (envUrl) return envUrl;

  const app = initFirebaseApplet();
  if (!app) {
    console.error(
      "ERROR: BUNKER DE DATOS NO ALCANZABLE. Firebase Storage no inicializado.",
    );
    return null;
  }

  const storage = getStorage(app);
  return getDownloadURL(ref(storage, SOVEREIGN_MESH_STORAGE_PATH));
}

export const loadSovereignMesh = async (): Promise<unknown | undefined> => {
  try {
    const url = await resolveSovereignMeshUrl();
    if (!url) {
      return undefined;
    }

    const meshData = await loadNinaMeshFromResponseStream(url);
    console.log("PA, PA, PA - MALLA SOBERANA CARGADA POR STREAM.");
    return meshData;
  } catch (error) {
    console.error("ERROR: BUNKER DE DATOS NO ALCANZABLE.", error);
    return undefined;
  }
};
