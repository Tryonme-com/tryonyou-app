import * as THREE from "three";
import { GLTFLoader } from "three/addons/loaders/GLTFLoader.js";

const DEFAULT_GLB = "/assets/models/pau_v11_high_poly.glb";

type LoadPauMasterModelOptions = {
  url?: string;
  onProgress?: (progress01: number) => void;
};

function createFabricMaterial(color: string, roughness = 0.42): THREE.MeshStandardMaterial {
  return new THREE.MeshStandardMaterial({
    color,
    roughness,
    metalness: 0.08,
    transparent: true,
    opacity: 0.96,
  });
}

export function createPauPreviewShell(): THREE.Group {
  const group = new THREE.Group();
  group.name = "pau-preview-shell";

  const palette = {
    gold: createFabricMaterial("#c9a76a", 0.38),
    champagne: createFabricMaterial("#efe2c7", 0.5),
    obsidian: createFabricMaterial("#1b1510", 0.62),
  };

  const torso = new THREE.Mesh(new THREE.CapsuleGeometry(0.18, 0.85, 8, 16), palette.gold);
  torso.position.set(0, -0.02, 0);

  const head = new THREE.Mesh(new THREE.SphereGeometry(0.18, 24, 24), palette.champagne);
  head.position.set(0, 0.78, 0.03);
  head.scale.set(0.92, 1.08, 0.94);

  const shoulderLine = new THREE.Mesh(new THREE.CylinderGeometry(0.3, 0.22, 0.12, 20), palette.obsidian);
  shoulderLine.rotation.z = Math.PI / 2;
  shoulderLine.position.set(0, 0.38, 0);

  const baseAura = new THREE.Mesh(
    new THREE.CircleGeometry(0.54, 40),
    new THREE.MeshBasicMaterial({
      color: "#d6b97b",
      transparent: true,
      opacity: 0.12,
      side: THREE.DoubleSide,
    }),
  );
  baseAura.rotation.x = -Math.PI / 2;
  baseAura.position.set(0, -0.76, 0);

  group.add(torso, head, shoulderLine, baseAura);
  return group;
}

function applyLuxuryFabricMaterials(root: THREE.Object3D): void {
  root.traverse((child) => {
    if (!(child instanceof THREE.Mesh)) return;
    child.castShadow = true;
    child.receiveShadow = true;
    const mats = Array.isArray(child.material) ? child.material : [child.material];
    for (const mat of mats) {
      if (mat instanceof THREE.MeshStandardMaterial) {
        mat.roughness = 0.4;
        mat.metalness = Math.min(mat.metalness, 0.12);
      }
    }
  });
}

export function loadPauMasterModel(
  scene: THREE.Object3D,
  options: LoadPauMasterModelOptions = {},
): Promise<THREE.Group> {
  const { url = DEFAULT_GLB, onProgress } = options;
  return new Promise((resolve, reject) => {
    const loader = new GLTFLoader();
    loader.load(
      url,
      (gltf) => {
        const model = gltf.scene;
        applyLuxuryFabricMaterials(model);
        scene.add(model);
        onProgress?.(1);
        resolve(model);
      },
      (event) => {
        if (!event.total) {
          onProgress?.(0.35);
          return;
        }
        const progress = Math.min(0.98, Math.max(0.08, event.loaded / event.total));
        onProgress?.(progress);
      },
      (err) => reject(err instanceof Error ? err : new Error(String(err))),
    );
  });
}
