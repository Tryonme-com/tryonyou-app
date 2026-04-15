/**
 * Avatar Pau tiempo real — GLB + animación procedural (pipeline compatible Kalidokit / MediaPipe).
 * Vídeo bajo el canvas hasta que el modelo3D cargue (evita “cartón” estático).
 */
import { useEffect, useRef, useState } from "react";
import * as THREE from "three";
import { loadPauMasterModel } from "../divineo/pauV11";

type Variant = "lafayette" | "marais";

type Props = {
  variant: Variant;
  disabled?: boolean;
  videoId: string;
};

function PauVideoFallback({ variant, videoId }: Pick<Props, "variant" | "videoId">) {
  return (
    <video
      key={variant}
      id={`${videoId}-fallback`}
      autoPlay
      loop
      muted
      playsInline
      preload="auto"
      style={{
        width: "100%",
        height: "100%",
        objectFit: "cover",
      }}
    >
      {variant === "marais" ? (
        <>
          <source src="/assets/marais_pau_v10.mp4" type="video/mp4" />
          <source src="/videos/pau_transparent.webm" type="video/webm" />
          <source src="/videos/pau_transparent.mp4" type="video/mp4" />
        </>
      ) : (
        <>
          <source src="/videos/pau_transparent.webm" type="video/webm" />
          <source src="/videos/pau_transparent.mp4" type="video/mp4" />
        </>
      )}
    </video>
  );
}

export default function RealTimeAvatar({ variant, disabled, videoId }: Props) {
  const containerRef = useRef<HTMLDivElement>(null);
  const glHostRef = useRef<HTMLDivElement>(null);
  const [glbReady, setGlbReady] = useState(false);

  useEffect(() => {
    if (disabled || !glHostRef.current) return;

    const mount = glHostRef.current;
    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(42, 1, 0.1, 100);
    camera.position.set(0, 0.05, 2.1);

    const renderer = new THREE.WebGLRenderer({
      alpha: true,
      antialias: true,
      powerPreference: "high-performance",
    });
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    const size = Math.max(mount.clientWidth, 1);
    renderer.setSize(size, size);
    renderer.setClearColor(0x000000, 0);
    mount.appendChild(renderer.domElement);

    const key = new THREE.DirectionalLight(0xfff5e6, 1.15);
    key.position.set(1.2, 2, 1.5);
    scene.add(key);
    scene.add(new THREE.AmbientLight(0xc5a46d, 0.35));

    let model: THREE.Group | null = null;
    let raf = 0;
    let alive = true;
    const clock = new THREE.Clock();

    const tick = () => {
      if (!alive) return;
      const t = clock.getElapsedTime();
      if (model) {
        model.rotation.y = Math.sin(t * 0.9) * 0.12;
        model.position.y = Math.sin(t * 1.4) * 0.02;
      }
      renderer.render(scene, camera);
      raf = requestAnimationFrame(tick);
    };

    void loadPauMasterModel(scene)
      .then((g) => {
        if (!alive) return;
        model = g;
        const box = new THREE.Box3().setFromObject(g);
        const ctr = box.getCenter(new THREE.Vector3());
        const sz = box.getSize(new THREE.Vector3());
        g.position.sub(ctr);
        const maxDim = Math.max(sz.x, sz.y, sz.z, 0.001);
        g.scale.setScalar(1.35 / maxDim);
        setGlbReady(true);
        tick();
      })
      .catch(() => {
        if (!alive) return;
        setGlbReady(false);
        cancelAnimationFrame(raf);
        scene.clear();
        renderer.dispose();
        if (renderer.domElement.parentNode === mount) {
          mount.removeChild(renderer.domElement);
        }
      });

    const ro = new ResizeObserver((entries) => {
      if (!alive) return;
      const cr = entries[0]?.contentRect;
      const s = cr ? Math.max(cr.width, 1) : Math.max(mount.clientWidth, 1);
      renderer.setSize(s, s);
      camera.aspect = 1;
      camera.updateProjectionMatrix();
    });
    ro.observe(mount);

    return () => {
      alive = false;
      cancelAnimationFrame(raf);
      ro.disconnect();
      scene.clear();
      renderer.dispose();
      if (renderer.domElement.parentNode === mount) {
        mount.removeChild(renderer.domElement);
      }
      setGlbReady(false);
    };
  }, [disabled, variant]);

  if (disabled) {
    return (
      <div style={{ width: "100%", height: "100%" }}>
        <PauVideoFallback variant={variant} videoId={videoId} />
      </div>
    );
  }

  return (
    <div
      ref={containerRef}
      style={{
        position: "relative",
        width: "100%",
        height: "100%",
        overflow: "hidden",
      }}
    >
      <div
        style={{
          position: "absolute",
          inset: 0,
          opacity: glbReady ? 0 : 1,
          transition: "opacity 0.45s ease-out",
          pointerEvents: "none",
          zIndex: 0,
        }}
      >
        <PauVideoFallback variant={variant} videoId={videoId} />
      </div>
      <div
        ref={glHostRef}
        style={{
          position: "relative",
          zIndex: 1,
          width: "100%",
          height: "100%",
        }}
      />
    </div>
  );
}
