/**
 * Maison Couture Nocturne — Video feature.
 * Wide cinematic video framed in mirror-frame.
 */
import { useRef, useState } from "react";

export default function VideoFeature() {
  const ref = useRef<HTMLVideoElement>(null);
  const [playing, setPlaying] = useState(false);

  const toggle = () => {
    const v = ref.current;
    if (!v) return;
    if (v.paused) {
      void v.play();
      setPlaying(true);
    } else {
      v.pause();
      setPlaying(false);
    }
  };

  return (
    <section className="relative py-24 md:py-36 bg-[var(--color-graphite)]">
      <div className="container">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-10 mb-12">
          <div className="lg:col-span-6 reveal-up">
            <span className="eyebrow mb-5 inline-flex">En mouvement</span>
            <h2 className="display-l">
              L'essayage
              <br />
              <span className="accent-italic">en images.</span>
            </h2>
          </div>
          <div className="lg:col-span-5 lg:col-start-8 lg:pt-6 reveal-up" data-delay="160">
            <p className="text-[16px] leading-[1.75] text-[var(--color-ivoire)]/80">
              Une démonstration cinématographique du parcours TRYONYOU&nbsp;:
              du scan biométrique au drapé textile temps réel, jusqu'à la
              recommandation finale projetée dans le miroir digital.
            </p>
          </div>
        </div>

        <div className="reveal-up">
          <div className="mirror-frame aspect-[16/9] overflow-hidden group">
            <video
              ref={ref}
              src="/images/demo-video.mp4"
              poster="/images/gemelo-digital.jpg"
              className="w-full h-full object-cover"
              playsInline
              loop
              preload="metadata"
              onClick={toggle}
            />
            {!playing && (
              <button
                aria-label="Lancer la vidéo"
                onClick={toggle}
                className="absolute inset-0 flex items-center justify-center bg-[rgba(10,8,7,0.45)] transition-opacity duration-700 group-hover:bg-[rgba(10,8,7,0.3)]"
              >
                <span className="flex flex-col items-center gap-4">
                  <span className="w-20 h-20 md:w-24 md:h-24 border border-[var(--color-or)] rounded-full flex items-center justify-center transition-transform duration-700 group-hover:scale-110">
                    <svg width="22" height="26" viewBox="0 0 22 26" fill="none">
                      <path d="M2 2 L20 13 L2 24 Z" fill="#C9A84C" />
                    </svg>
                  </span>
                  <span className="text-[11px] tracking-[0.28em] uppercase text-[var(--color-or)]">
                    Lancer la démo
                  </span>
                </span>
              </button>
            )}
          </div>
        </div>
      </div>
    </section>
  );
}
