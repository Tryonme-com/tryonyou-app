/**
 * Actualización de texturas de belleza — Pau V11 (maquillaje / peinado sobre malla Three.js).
 * Los assets son opcionales: si faltan rutas bajo `public/`, el visor sigue operativo.
 *
 * Patente PCT/EP2025/067317 — @CertezaAbsoluta @lo+erestu
 * Bajo Protocolo de Soberanía V10 - Founder: Rubén
 */
import * as THREE from "three";
import { GLTFLoader } from "three/addons/loaders/GLTFLoader.js";

export type BeautyLookContext = "MASTER_LOOK" | "POOL_EXIT";

const EYESHADOW_TEX = "/assets/beauty/smokey_versace.png";
const HAIR_GLB = "/assets/models/greek_updo_simple.glb";

function isFaceLikeMeshName(name: string): boolean {
  const n = name.toLowerCase();
  return /face|head|cabeza|rostro|skin|ojos|eye|brow|ceja/i.test(n);
}

function isHairMeshName(name: string): boolean {
  const n = name.toLowerCase();
  return /hair|pelo|cabello|pony|bun|updo/i.test(n);
}

function standardMats(mesh: THREE.Mesh): THREE.MeshStandardMaterial[] {
  const raw = Array.isArray(mesh.material) ? mesh.material : [mesh.material];
  return raw.filter((m): m is THREE.MeshStandardMaterial => m instanceof THREE.MeshStandardMaterial);
}

async function tryLoadEyeshadow(): Promise<THREE.Texture | null> {
  try {
    const tex = await new THREE.TextureLoader().loadAsync(EYESHADOW_TEX);
    tex.colorSpace = THREE.SRGBColorSpace;
    tex.flipY = false;
    return tex;
  } catch {
    if (import.meta.env.DEV) {
      console.warn("[Divineo] Maquillaje opcional no cargado:", EYESHADOW_TEX);
    }
    return null;
  }
}

async function tryAttachGreekUpdo(avatar: THREE.Object3D): Promise<void> {
  try {
    const gltf = await new GLTFLoader().loadAsync(HAIR_GLB);
    const hair = gltf.scene;
    hair.name = "pau_beauty:greek_updo_simple";
    hair.traverse((c) => {
      if (c instanceof THREE.Mesh) {
        c.castShadow = true;
        c.receiveShadow = true;
      }
    });
    avatar.add(hair);
  } catch {
    if (import.meta.env.DEV) {
      console.warn("[Divineo] Peinado GLB opcional no cargado:", HAIR_GLB);
    }
  }
}

/**
 * Aplica look de belleza según contexto (Grecia / salida piscina) sobre el grupo del avatar Pau.
 */
export async function applyMasterBeautyLook(
  avatar: THREE.Object3D,
  context: BeautyLookContext,
): Promise<void> {
  const eyeshadow = await tryLoadEyeshadow();

  avatar.traverse((child) => {
    if (!(child instanceof THREE.Mesh)) return;
    const mats = standardMats(child);
    for (const mat of mats) {
      if (isFaceLikeMeshName(child.name) && eyeshadow) {
        mat.emissiveMap = eyeshadow;
        mat.emissive = new THREE.Color(0x8866aa);
        mat.emissiveIntensity = 0.22;
      }
      if (isHairMeshName(child.name) && context === "POOL_EXIT") {
        mat.roughness = Math.min(0.92, (mat.roughness ?? 0.45) * 0.38);
        mat.metalness = Math.min(0.28, (mat.metalness ?? 0) + 0.12);
        mat.envMapIntensity = (mat.envMapIntensity ?? 1) * 1.15;
      }
    }
  });

  if (context === "MASTER_LOOK") {
    await tryAttachGreekUpdo(avatar);
  }

  if (import.meta.env.DEV) {
    console.info("[Divineo] Maquillaje y peinado sellados · contexto:", context);
  }
}
