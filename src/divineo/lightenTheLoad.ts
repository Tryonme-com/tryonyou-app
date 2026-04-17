/**
 * Limpieza de memoria y cierre del stage WebGL — Espejo Divineo (evita residuos de mallas / texturas).
 * `powerPreference` solo aplica en la **creación** del renderer (ver `sovereignWebGLOptions`).
 *
 * Patente PCT/EP2025/067317 — @CertezaAbsoluta @lo+erestu
 * Bajo Protocolo de Soberanía V10 - Founder: Rubén
 */
import * as THREE from "three";

function disposeMeshLike(obj: THREE.Object3D): void {
  if (!(obj instanceof THREE.Mesh)) return;
  const mesh = obj;
  mesh.geometry?.dispose();
  const mats = Array.isArray(mesh.material) ? mesh.material : [mesh.material];
  for (const m of mats) {
    if (m && typeof (m as THREE.Material).dispose === "function") {
      (m as THREE.Material).dispose();
    }
  }
}

function disposeSubtree(root: THREE.Object3D): void {
  root.traverse((o) => disposeMeshLike(o));
}

/**
 * Retira y dispone recursos GPU de todos los hijos de la escena, luego destruye el contexto WebGL del renderer.
 */
export function lightenTheLoad(scene: THREE.Scene, renderer: THREE.WebGLRenderer): void {
  const snapshot = [...scene.children];
  for (const child of snapshot) {
    scene.remove(child);
    disposeSubtree(child);
  }
  renderer.dispose();
  if (import.meta.env.DEV) {
    console.info("[Soberanía] Peso eliminado. Stage Divineo liberado.");
  }
}

/** Opciones de creación alineadas con alto rendimiento (no mutables después). */
export function sovereignWebGLOptions(): THREE.WebGLRendererParameters {
  return {
    alpha: true,
    antialias: true,
    powerPreference: "high-performance",
  };
}

/**
 * DPR capado: espejos muy anchos (> 2 m en CSS px aprox.) bajan techo para mantener frame estable.
 */
export function applySovereignPixelRatio(
  renderer: THREE.WebGLRenderer,
  mirrorWidthCssPx: number,
): void {
  const wide = mirrorWidthCssPx > 2000;
  const cap = wide ? 1.5 : 2;
  const dpr = window.devicePixelRatio > 1 ? Math.min(window.devicePixelRatio, cap) : 1;
  renderer.setPixelRatio(dpr);
}
