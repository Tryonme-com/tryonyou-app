/**
 * 🛡️ EXTRACCIÓN DE BIOMETRÍA - TRYONYOU1
 * Criba de datos para proyección Robert Engine
 *
 * Patente PCT/EP2025/067317 — @CertezaAbsoluta @lo+erestu
 * Bajo Protocolo de Soberanía V10 - Founder: Rubén
 */
import { getStorage, ref, getDownloadURL } from "firebase/storage";
import { initFirebaseApplet } from "./firebaseApplet";

const app = initFirebaseApplet();
const storage = app ? getStorage(app) : null;
const biometricRef = storage
  ? ref(storage, "biometria/nina_perfecta_mesh.json")
  : null;

export const loadSovereignMesh = async (): Promise<unknown> => {
  if (!biometricRef) {
    console.error("ERROR: BÚNKER DE DATOS NO ALCANZABLE.");
    return undefined;
  }
  try {
    const url = await getDownloadURL(biometricRef);
    const response = await fetch(url);
    const meshData: unknown = await response.json();
    console.log("PA, PA, PA - MALLA DE 111MB CARGADA. PROYECTANDO CERTEZA.");
    return meshData;
  } catch (error) {
    console.error("ERROR: BÚNKER DE DATOS NO ALCANZABLE.");
    return undefined;
  }
};
