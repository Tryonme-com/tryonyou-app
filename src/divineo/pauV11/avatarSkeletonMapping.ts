/**
 * Mapeo tiempo real: landmarks MediaPipe (Holistic / Pose) → Kalidokit solvers → rig Three.js.
 *
 * Flujo: captura → `Kalidokit.Pose.solve` / `Hand.solve` / `Face.solve` → rotaciones (grados)
 * → aplicar a `THREE.Bone` del GLB Pau V11. Ajusta `PAU_V11_BONE_MAP` al naming del .glb.
 *
 * Referencia diagramas skeleton: convención Kalidokit (articulaciones tipo Mixamo).
 */
import * as THREE from "three";

export const DEG2RAD = Math.PI / 180;

export type KalidokitRotation = { x: number; y: number; z: number };

/** Convierte salida Kalidokit (grados) a Euler Three. */
export function kalidokitToEuler(
  r: KalidokitRotation,
  order: THREE.EulerOrder = "YXZ",
): THREE.Euler {
  return new THREE.Euler(
    r.x * DEG2RAD,
    r.y * DEG2RAD,
    r.z * DEG2RAD,
    order,
  );
}

/**
 * Claves Kalidokit.Pose.solve → nombres de hueso en el GLB (ej. mixamorig*).
 * Sustituye por los nombres reales tras inspeccionar `pau_v11_high_poly.glb`.
 */
export const PAU_V11_BONE_MAP: Record<string, string> = {
  Hips: "mixamorigHips",
  Spine: "mixamorigSpine",
  Spine1: "mixamorigSpine1",
  Spine2: "mixamorigSpine2",
  Neck: "mixamorigNeck",
  Head: "mixamorigHead",
  LeftShoulder: "mixamorigLeftShoulder",
  RightShoulder: "mixamorigRightShoulder",
  LeftUpperArm: "mixamorigLeftArm",
  RightUpperArm: "mixamorigRightArm",
  LeftLowerArm: "mixamorigLeftForeArm",
  RightLowerArm: "mixamorigRightForeArm",
  LeftHand: "mixamorigLeftHand",
  RightHand: "mixamorigRightHand",
  LeftUpperLeg: "mixamorigLeftUpLeg",
  RightUpperLeg: "mixamorigRightUpLeg",
  LeftLowerLeg: "mixamorigLeftLeg",
  RightLowerLeg: "mixamorigRightLeg",
  LeftFoot: "mixamorigLeftFoot",
  RightFoot: "mixamorigRightFoot",
};

/** Resuelve mapa Kalidokit → Object3D por nombre en el grafo del modelo. */
export function resolvePauBones(
  modelRoot: THREE.Object3D,
  map: Record<string, string> = PAU_V11_BONE_MAP,
): Map<string, THREE.Object3D> {
  const out = new Map<string, THREE.Object3D>();
  for (const [kKey, gltfName] of Object.entries(map)) {
    const obj = modelRoot.getObjectByName(gltfName);
    if (obj) out.set(kKey, obj);
  }
  return out;
}

/**
 * Aplica `pose` devuelto por Kalidokit.Pose.solve sobre huesos ya resueltos.
 * Solo actualiza claves presentes en ambos lados.
 */
export function applyKalidokitPoseToSkeleton(
  pose: Record<string, KalidokitRotation | undefined>,
  bonesByKalidokitKey: Map<string, THREE.Object3D>,
): void {
  for (const [key, rot] of Object.entries(pose)) {
    if (!rot) continue;
    const bone = bonesByKalidokitKey.get(key);
    if (!bone) continue;
    bone.rotation.copy(kalidokitToEuler(rot));
  }
}
