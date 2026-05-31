/**
 * Cámara virtual Divineo — Soberanía «Vogue style»: FOV nítido, encuadre textil, calidad render.
 * Contrato operativo para `PerspectiveCamera` (Three.js); el aspect real sigue al contenedor.
 *
 * Patente PCT/EP2025/067317 — @CertezaAbsoluta @lo+erestu
 * Bajo Protocolo de Soberanía V10 - Founder: Rubén
 */
import * as THREE from "three";

export type DivineoCameraQuality = "MASTERPIECE_ULTRA";

export const DIVINEO_SOVEREIGN_CAMERA = {
  /** Referencia estética ultrawide (marca); no fuerza letterbox en el slot cuadrado actual. */
  aspectRatioLabel: "21:9" as const,
  fieldOfViewDeg: 45,
  /** Distancia de trabajo declarada para lectura de textura (50 cm; narrativa / futuro DOF). */
  idealSubjectDistanceM: 0.5,
  nearPlane: 0.1,
  farPlane: 100,
  qualityLevel: "MASTERPIECE_ULTRA" as DivineoCameraQuality,
  position: { x: 0, y: 0.05, z: 2.1 },
} as const;

export function createDivineoPerspectiveCamera(
  widthPx: number,
  heightPx: number,
): THREE.PerspectiveCamera {
  const cam = new THREE.PerspectiveCamera(
    DIVINEO_SOVEREIGN_CAMERA.fieldOfViewDeg,
    Math.max(1, widthPx) / Math.max(1, heightPx),
    DIVINEO_SOVEREIGN_CAMERA.nearPlane,
    DIVINEO_SOVEREIGN_CAMERA.farPlane,
  );
  const p = DIVINEO_SOVEREIGN_CAMERA.position;
  cam.position.set(p.x, p.y, p.z);
  if (import.meta.env.DEV) {
    console.info(
      "[Mando] Cámara Divineo: FOV",
      DIVINEO_SOVEREIGN_CAMERA.fieldOfViewDeg,
      "· relación ref.",
      DIVINEO_SOVEREIGN_CAMERA.aspectRatioLabel,
      "·",
      DIVINEO_SOVEREIGN_CAMERA.qualityLevel,
    );
  }
  return cam;
}

export function resizeDivineoPerspectiveCamera(
  camera: THREE.PerspectiveCamera,
  widthPx: number,
  heightPx: number,
): void {
  camera.aspect = Math.max(1, widthPx) / Math.max(1, heightPx);
  camera.updateProjectionMatrix();
}
