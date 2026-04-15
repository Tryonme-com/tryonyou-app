import { useEffect, useRef, useState } from "react";
import * as THREE from "three";
import { createPauPreviewShell, loadPauMasterModel } from "../divineo/pauV11";
import { fetchModelAccessToken } from "../lib/coreEngineClient";

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
  const [previewReady, setPreviewReady] = useState(false);
  const [loadProgress, setLoadProgress] = useState(0);

  useEffect(() => {
    if (disabled || !glHostRef.current) return;

    const mount = glHostRef.current;
    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(42, 1, 0.1, 100);
    camera.position.set(0, 0.05, 2.1);

    const renderer = new THREE.WebGLRenderer({
      alpha: true,
      antialias: false,
      powerPreference: "high-performance",
    });
    renderer.outputColorSpace = THREE.SRGBColorSpace;
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 1.25));
    const size = Math.max(mount.clientWidth, 1);
    renderer.setSize(size, size);
    renderer.setClearColor(0x000000, 0);
    mount.appendChild(renderer.domElement);

    const key = new THREE.DirectionalLight(0xfff5e6, 1.15);
    key.position.set(1.2, 2, 1.5);
    const rim = new THREE.PointLight(0xd2b47c, 0.8, 4.5);
    rim.position.set(-1.1, 0.9, 1.25);
    scene.add(key);
    scene.add(rim);
    scene.add(new THREE.AmbientLight(0xc5a46d, 0.35));

    let model: THREE.Group | null = null;
    let preview: THREE.Group | null = createPauPreviewShell();
    preview.position.set(0, -0.08, 0);
    scene.add(preview);

    let raf = 0;
    let alive = true;
    const clock = new THREE.Clock();

    const activeRenderable = () => model ?? preview;

    const tick = () => {
      if (!alive) return;
      const t = clock.getElapsedTime();
      const target = activeRenderable();
      if (target) {
        target.rotation.y = Math.sin(t * 0.9) * 0.12;
        target.position.y = Math.sin(t * 1.4) * 0.02 + (target === model ? 0 : -0.08);
      }
      renderer.render(scene, camera);
      raf = requestAnimationFrame(tick);
    };

    setPreviewReady(true);
    setLoadProgress(0.08);
    tick();

    void (async () => {
      const access = await fetchModelAccessToken({
        model_id: "pau_v11",
        variant,
      });
      if (!alive || !access?.ok || !access.access_token) {
        setLoadProgress(0.22);
        return;
      }
      const baseUrl = String(
        import.meta.env.VITE_PAU_MASTER_MODEL_URL ?? "/assets/models/pau_v11_high_poly.glb",
      );
      const url = `${baseUrl}${baseUrl.includes("?") ? "&" : "?"}access_token=${encodeURIComponent(access.access_token)}`;
      loadPauMasterModel(scene, {
        url,
        onProgress: (progress01) => {
          if (!alive) return;
          setLoadProgress(progress01);
        },
      })
        .then((g) => {
          if (!alive) return;
          model = g;
          const box = new THREE.Box3().setFromObject(g);
          const ctr = box.getCenter(new THREE.Vector3());
          const sz = box.getSize(new THREE.Vector3());
          g.position.sub(ctr);
          const maxDim = Math.max(sz.x, sz.y, sz.z, 0.001);
          g.scale.setScalar(1.35 / maxDim);
          renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
          if (preview) {
            scene.remove(preview);
            preview.traverse((child) => {
              if (!(child instanceof THREE.Mesh)) return;
              child.geometry.dispose();
              const materials = Array.isArray(child.material) ? child.material : [child.material];
              for (const material of materials) {
                material.dispose();
              }
            });
            preview = null;
          }
          setLoadProgress(1);
          setGlbReady(true);
        })
        .catch(() => {
          if (!alive) return;
          setGlbReady(false);
        });
    })();

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
      setPreviewReady(false);
      setGlbReady(false);
      setLoadProgress(0);
    };
  }, [disabled, variant]);

  if (disabled) {
    return (
      <div style={{ width: "100%", height: "100%" }}>
        <PauVideoFallback variant={variant} videoId={videoId} />
      </div>
    );
  }

  const fallbackOpacity = glbReady ? 0 : previewReady ? 0.26 : 1;

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
          opacity: fallbackOpacity,
          transition: "opacity 0.35s ease-out",
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
      {!glbReady ? (
        <div
          aria-hidden="true"
          style={{
            position: "absolute",
            right: 14,
            bottom: 14,
            zIndex: 2,
            padding: "8px 10px",
            borderRadius: 999,
            background: "rgba(14, 10, 8, 0.44)",
            color: "#D3B26A",
            fontSize: 10,
            letterSpacing: 1.4,
            textTransform: "uppercase",
            backdropFilter: "blur(8px)",
          }}
        >
          {`P.A.U. ${Math.round(loadProgress * 100)}%`}
        </div>
      ) : null}
    </div>
  );
}
