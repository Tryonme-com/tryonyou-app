/**
 * Avatar Pau tiempo real — GLB + animación procedural (pipeline compatible Kalidokit / MediaPipe).
 * Vídeo bajo el canvas hasta que el modelo3D cargue (evita “cartón” estático).
 */
import { useEffect, useRef, useState } from "react";
import * as THREE from "three";
import { applyMasterBeautyLook, loadPauMasterModel } from "../divineo/pauV11";
import {
  applySovereignPixelRatio,
  lightenTheLoad,
  sovereignWebGLOptions,
} from "../divineo/lightenTheLoad";
import {
  createDivineoPerspectiveCamera,
  resizeDivineoPerspectiveCamera,
} from "../divineo/setupDivineoCamera";
import { applyVerticalMirrorVersaceCalibration } from "../divineo/mirrorCalibrationVersace";

type Variant = "lafayette" | "marais";

type Props = {
  variant: Variant;
  disabled?: boolean;
  videoId: string;
  /** Espejo vertical >2 m — calibración Versace (FOV, pitch, aspect retrato). */
  verticalVersaceMirror?: boolean;
};

function PauVideoFallback({
  variant,
  videoId,
  verticalVersaceMirror,
}: Pick<Props, "variant" | "videoId" | "verticalVersaceMirror">) {
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
        objectPosition: verticalVersaceMirror ? "center 28%" : "center center",
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

export default function RealTimeAvatar({
  variant,
  disabled,
  videoId,
  verticalVersaceMirror = false,
}: Props) {
  const containerRef = useRef<HTMLDivElement>(null);
  const glHostRef = useRef<HTMLDivElement>(null);
  const [glbReady, setGlbReady] = useState(false);

  useEffect(() => {
    if (disabled || !glHostRef.current) return;

    const mount = glHostRef.current;
    const scene = new THREE.Scene();
    const rw0 = Math.max(mount.clientWidth, 1);
    const rh0 = Math.max(mount.clientHeight, 1);
    const size0 = rw0;
    const camW = verticalVersaceMirror ? rw0 : size0;
    const camH = verticalVersaceMirror ? rh0 : size0;
    const camera = createDivineoPerspectiveCamera(camW, camH);
    if (verticalVersaceMirror) {
      applyVerticalMirrorVersaceCalibration(camera, camW, camH);
    }

    const renderer = new THREE.WebGLRenderer(sovereignWebGLOptions());
    const size = Math.max(mount.clientWidth, 1);
    applySovereignPixelRatio(renderer, size);
    renderer.setSize(rw0, rh0);
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

    const beautyCtx = variant === "marais" ? "POOL_EXIT" : "MASTER_LOOK";
    void loadPauMasterModel(scene)
      .then(async (g) => {
        if (!alive) return;
        model = g;
        const box = new THREE.Box3().setFromObject(g);
        const ctr = box.getCenter(new THREE.Vector3());
        const sz = box.getSize(new THREE.Vector3());
        g.position.sub(ctr);
        const maxDim = Math.max(sz.x, sz.y, sz.z, 0.001);
        g.scale.setScalar(1.35 / maxDim);
        try {
          await applyMasterBeautyLook(g, beautyCtx);
        } catch {
          /* look opcional: no bloquea el visor */
        }
        if (!alive) return;
        setGlbReady(true);
        tick();
      })
      .catch(() => {
        if (!alive) return;
        setGlbReady(false);
        cancelAnimationFrame(raf);
        lightenTheLoad(scene, renderer);
        if (renderer.domElement.parentNode === mount) {
          mount.removeChild(renderer.domElement);
        }
      });

    const ro = new ResizeObserver(() => {
      const el = containerRef.current;
      const w = Math.max(mount.clientWidth, 1);
      const h = Math.max(mount.clientHeight, 1);
      const s = el ? Math.max(el.clientWidth, 1) : w;
      applySovereignPixelRatio(renderer, s);
      renderer.setSize(w, h);
      if (verticalVersaceMirror) {
        applyVerticalMirrorVersaceCalibration(camera, w, h);
      } else {
        resizeDivineoPerspectiveCamera(camera, w, w);
      }
    });
    ro.observe(containerRef.current ?? mount);

    return () => {
      alive = false;
      cancelAnimationFrame(raf);
      ro.disconnect();
      lightenTheLoad(scene, renderer);
      if (renderer.domElement.parentNode === mount) {
        mount.removeChild(renderer.domElement);
      }
      setGlbReady(false);
    };
  }, [disabled, variant, verticalVersaceMirror]);

  if (disabled) {
    return (
      <div style={{ width: "100%", height: "100%" }}>
        <PauVideoFallback
          variant={variant}
          videoId={videoId}
          verticalVersaceMirror={verticalVersaceMirror}
        />
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
        <PauVideoFallback
          variant={variant}
          videoId={videoId}
          verticalVersaceMirror={verticalVersaceMirror}
        />
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
