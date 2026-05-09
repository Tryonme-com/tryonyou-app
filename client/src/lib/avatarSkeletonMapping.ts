/**
 * Avatar skeleton mapping — port from `Tryonme-com/tryonyou-app`
 * (src/divineo/pauV11/avatarSkeletonMapping.ts)
 *
 * Real-time pipeline: MediaPipe landmarks → Kalidokit solvers → Three.js bones.
 */
import * as THREE from "three";

export const DEG2RAD = Math.PI / 180;

export type KalidokitRotation = { x: number; y: number; z: number };

export function kalidokitToEuler(
  r: KalidokitRotation,
  order: THREE.EulerOrder = "YXZ",
): THREE.Euler {
  return new THREE.Euler(r.x * DEG2RAD, r.y * DEG2RAD, r.z * DEG2RAD, order);
}

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

export function resolvePauBones(
  modelRoot: THREE.Object3D,
  map: Record<string, string> = PAU_V11_BONE_MAP,
): Map<string, THREE.Object3D> {
  const out = new Map<string, THREE.Object3D>();
  for (const [k, gltfName] of Object.entries(map)) {
    const obj = modelRoot.getObjectByName(gltfName);
    if (obj) out.set(k, obj);
  }
  return out;
}

export function applyKalidokitPoseToSkeleton(
  pose: Record<string, KalidokitRotation | undefined>,
  bones: Map<string, THREE.Object3D>,
): void {
  for (const [k, rot] of Object.entries(pose)) {
    if (!rot) continue;
    const bone = bones.get(k);
    if (!bone) continue;
    bone.rotation.copy(kalidokitToEuler(rot));
  }
}
