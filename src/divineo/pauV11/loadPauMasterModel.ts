/**
 * Visor 3D Pau V11 — carga GLB de alta fidelidad + ajuste de materiales (telas, no plástico).
 * Kalidokit: exportado desde `pauV11/index.ts` como `Kalidokit` (namespace).
 */
import * as THREE from "three";
import { GLTFLoader } from "three/addons/loaders/GLTFLoader.js";

const DEFAULT_GLB = "/assets/models/pau_v11_high_poly.glb";

function applyLuxuryFabricMaterials(root: THREE.Object3D): void {
  root.traverse((child) => {
    if (!(child instanceof THREE.Mesh)) return;
    child.castShadow = true;
    child.receiveShadow = true;
    const mats = Array.isArray(child.material)
      ? child.material
      : [child.material];
    for (const mat of mats) {
      if (mat instanceof THREE.MeshStandardMaterial) {
        mat.roughness = 0.4;
      }
    }
  });
}

export function loadPauMasterModel(
  scene: THREE.Object3D,
  url: string = DEFAULT_GLB,
): Promise<THREE.Group> {
  return new Promise((resolve, reject) => {
    const loader = new GLTFLoader();
    loader.load(
      url,
      (gltf) => {
        const model = gltf.scene;
        applyLuxuryFabricMaterials(model);
        scene.add(model);
        resolve(model);
      },
      undefined,
      (err) => reject(err instanceof Error ? err : new Error(String(err))),
    );
  });
}
