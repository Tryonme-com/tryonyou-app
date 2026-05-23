import * as THREE from "three";

export type ThreeSceneRefs = {
  scene: THREE.Scene;
  camera: THREE.PerspectiveCamera;
  renderer: THREE.WebGLRenderer;
  bones: Record<string, THREE.Object3D>;
  rig: THREE.Group;
};

export function setupThreeRig(host: HTMLDivElement): {
  refs: ThreeSceneRefs;
  cleanup: () => void;
} {
  const scene = new THREE.Scene();
  scene.background = null;

  const camera = new THREE.PerspectiveCamera(38, 1, 0.1, 100);
  camera.position.set(0, 0.05, 2.6);

  const renderer = new THREE.WebGLRenderer({
    alpha: true,
    antialias: true,
    powerPreference: "high-performance",
  });
  renderer.outputColorSpace = THREE.SRGBColorSpace;
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
  const size = Math.max(host.clientWidth, 1);
  renderer.setSize(size, size);
  renderer.setClearColor(0x000000, 0);
  host.appendChild(renderer.domElement);

  // Lighting — couture warm
  scene.add(new THREE.AmbientLight(0xc5a46d, 0.4));
  const key = new THREE.DirectionalLight(0xfff5e6, 1.1);
  key.position.set(1.2, 2, 1.5);
  scene.add(key);
  const rim = new THREE.PointLight(0xc9a84c, 1.0, 5);
  rim.position.set(-1.2, 0.8, 1.4);
  scene.add(rim);

  // Articulated wireframe — couture gold mannequin
  const goldMat = new THREE.MeshStandardMaterial({
    color: 0xc9a84c,
    roughness: 0.3,
    metalness: 0.6,
    emissive: 0x4a3a18,
    emissiveIntensity: 0.4,
  });
  const ivoryMat = new THREE.MeshStandardMaterial({
    color: 0xefe2c7,
    roughness: 0.5,
    metalness: 0.1,
  });
  const obsidianMat = new THREE.MeshStandardMaterial({
    color: 0x1b1510,
    roughness: 0.62,
    metalness: 0.2,
  });

  const rig = new THREE.Group();
  rig.name = "pau-couture-rig";

  // hips
  const hips = new THREE.Group();
  hips.name = "Hips";
  rig.add(hips);

  // spine + torso
  const spine = new THREE.Group();
  spine.name = "Spine";
  spine.position.y = 0.05;
  hips.add(spine);
  const torso = new THREE.Mesh(
    new THREE.CapsuleGeometry(0.16, 0.65, 8, 16),
    goldMat
  );
  torso.position.y = 0.42;
  spine.add(torso);

  // Neck + head
  const neck = new THREE.Group();
  neck.name = "Neck";
  neck.position.y = 0.82;
  spine.add(neck);
  const head = new THREE.Mesh(new THREE.SphereGeometry(0.16, 24, 24), ivoryMat);
  head.position.y = 0.16;
  head.scale.set(0.92, 1.08, 0.94);
  neck.add(head);

  // Shoulders
  const lShoulder = new THREE.Group();
  lShoulder.name = "LeftShoulder";
  lShoulder.position.set(-0.22, 0.7, 0);
  spine.add(lShoulder);
  const rShoulder = new THREE.Group();
  rShoulder.name = "RightShoulder";
  rShoulder.position.set(0.22, 0.7, 0);
  spine.add(rShoulder);

  // Arms
  const buildArm = (group: THREE.Group, side: "L" | "R") => {
    const upper = new THREE.Mesh(
      new THREE.CapsuleGeometry(0.04, 0.28, 4, 8),
      obsidianMat
    );
    upper.position.y = -0.18;
    group.add(upper);
    const elbow = new THREE.Group();
    elbow.name = side === "L" ? "LeftLowerArm" : "RightLowerArm";
    elbow.position.y = -0.36;
    group.add(elbow);
    const lower = new THREE.Mesh(
      new THREE.CapsuleGeometry(0.035, 0.26, 4, 8),
      obsidianMat
    );
    lower.position.y = -0.16;
    elbow.add(lower);
  };
  buildArm(lShoulder, "L");
  buildArm(rShoulder, "R");

  // Legs
  const buildLeg = (xpos: number, name: string) => {
    const hip = new THREE.Group();
    hip.name = name;
    hip.position.set(xpos, -0.05, 0);
    hips.add(hip);
    const upper = new THREE.Mesh(
      new THREE.CapsuleGeometry(0.05, 0.36, 4, 8),
      goldMat
    );
    upper.position.y = -0.22;
    hip.add(upper);
    const knee = new THREE.Group();
    knee.name = name === "LeftUpperLeg" ? "LeftLowerLeg" : "RightLowerLeg";
    knee.position.y = -0.46;
    hip.add(knee);
    const lower = new THREE.Mesh(
      new THREE.CapsuleGeometry(0.045, 0.34, 4, 8),
      goldMat
    );
    lower.position.y = -0.2;
    knee.add(lower);
  };
  buildLeg(-0.09, "LeftUpperLeg");
  buildLeg(0.09, "RightUpperLeg");

  // Aura under feet
  const aura = new THREE.Mesh(
    new THREE.CircleGeometry(0.55, 40),
    new THREE.MeshBasicMaterial({
      color: 0xc9a84c,
      transparent: true,
      opacity: 0.15,
      side: THREE.DoubleSide,
    })
  );
  aura.rotation.x = -Math.PI / 2;
  aura.position.y = -0.95;
  rig.add(aura);

  rig.position.y = 0.12;
  scene.add(rig);

  // Resolve named bones for the Kalidokit mapping
  const bones: Record<string, THREE.Object3D> = {};
  rig.traverse((o: THREE.Object3D) => {
    if (o.name) bones[o.name] = o;
  });

  const refs: ThreeSceneRefs = { scene, camera, renderer, bones, rig };

  const ro = new ResizeObserver(entries => {
    const cr = entries[0]?.contentRect;
    const ss = cr ? Math.max(cr.width, 1) : Math.max(host.clientWidth, 1);
    renderer.setSize(ss, ss);
    camera.aspect = 1;
    camera.updateProjectionMatrix();
  });
  ro.observe(host);

  const cleanup = () => {
    ro.disconnect();
    renderer.dispose();
    scene.clear();
    if (renderer.domElement.parentNode) {
      renderer.domElement.parentNode.removeChild(renderer.domElement);
    }
  };

  return { refs, cleanup };
}
