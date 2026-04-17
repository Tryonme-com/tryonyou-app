/**
 * Calibración espejo vertical Versace — montaje físico típico >2 m, encuadre esbelto (figura alargada).
 * Ajusta FOV, pitch y aspecto retrato del contenedor para lectura «runway» en Three.js.
 *
 * Patente PCT/EP2025/067317 — @CertezaAbsoluta @lo+erestu
 * Bajo Protocolo de Soberanía V10 - Founder: Rubén
 */
import * as THREE from "three";

/** Referencia de instalación: espejo / sensor por encima de 2 m (briefing visualización esbelta). */
export const VERSACE_MIRROR_MOUNT_MIN_HEIGHT_M = 2.0;

/** FOV más cerrado que el Divineo genérico: silueta más larga en el encuadre. */
export const VERSACE_VERTICAL_MIRROR_FOV_DEG = 38;

/** Cámara alta mira ligeramente hacia el sujeto (espejo vertical real). */
export const VERSACE_HIGH_MOUNT_PITCH_RAD = 0.088;

export const VERSACE_CAMERA_POSITION = {
  x: 0,
  y: 0.14,
  z: 2.28,
} as const;

/**
 * Aplica calibración tras crear `PerspectiveCamera` (aspect = ancho/alto del slot espejo).
 */
export function applyVerticalMirrorVersaceCalibration(
  camera: THREE.PerspectiveCamera,
  widthPx: number,
  heightPx: number,
): void {
  const w = Math.max(1, widthPx);
  const h = Math.max(1, heightPx);
  camera.fov = VERSACE_VERTICAL_MIRROR_FOV_DEG;
  camera.aspect = w / h;
  camera.position.set(
    VERSACE_CAMERA_POSITION.x,
    VERSACE_CAMERA_POSITION.y,
    VERSACE_CAMERA_POSITION.z,
  );
  camera.rotation.order = "YXZ";
  camera.rotation.set(VERSACE_HIGH_MOUNT_PITCH_RAD, 0, 0);
  camera.updateProjectionMatrix();
}
