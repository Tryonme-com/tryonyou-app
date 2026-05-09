/**
 * Maison Couture Nocturne — Boutique Video section.
 * "L'Expérience en Boutique" — paloma-lafayette.mp4
 * Asymmetric layout: video left (col 1-7), editorial copy right (col 9-12).
 */
import { useRef, useState } from "react";

export default function BoutiqueVideo() {
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
    <section className="relative py-24 md:py-36">
      <div className="container">
        <div className="hairline mb-16 reveal-up" />

        <div className="grid grid-cols-1 lg:grid-cols-12 gap-10 lg:gap-16 items-center">
          {/* Video left */}
          <div className="lg:col-span-7 reveal-up">
            <div className="mirror-frame aspect-[9/16] sm:aspect-[3/4] lg:aspect-[9/16] overflow-hidden group">
              <video
                ref={ref}
                src="/images/paloma-lafayette.mp4"
                poster="/images/mirror-smart.jpg"
                className="w-full h-full object-contain"
                style={{ background: "var(--color-noir)" }}
                playsInline
                loop
                preload="metadata"
                onClick={toggle}
              />
              {!playing && (
                <button
                  aria-label="Lancer la vidéo boutique"
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
                      Lancer la vidéo
                    </span>
                  </span>
                </button>
              )}

              {/* Corner label */}
              <div className="absolute top-4 left-4 right-4 flex items-center justify-between text-[10px] tracking-[0.24em] uppercase text-[var(--color-or)]">
                <span>En boutique · Live</span>
                <span className="inline-flex items-center gap-2">
                  <span className="w-1.5 h-1.5 rounded-full bg-[var(--color-or)] animate-pulse" />
                  Paloma Lafayette
                </span>
              </div>
            </div>
          </div>

          {/* Editorial copy right */}
          <div className="lg:col-span-4 lg:col-start-9 reveal-up" data-delay="200">
            <span className="eyebrow mb-5 inline-flex">L'expérience en boutique</span>
            <h2 className="display-l mb-6">
              Le miroir
              <br />
              <span className="accent-italic">qui convainc.</span>
            </h2>
            <p className="text-[17px] leading-[1.75] text-[var(--color-ivoire)]/80 mb-8">
              En boutique comme en ligne, TRYONYOU transforme chaque essayage en
              moment de certitude. Le client voit sa silhouette réelle habillée de
              la pièce exacte — sans hésitation, sans retour.
            </p>

            <ul className="space-y-4 text-[14px] mb-10">
              {[
                "Détection silhouette en moins de 2 secondes",
                "Overlay vêtement photoréaliste temps réel",
                "Recommandation look complet par le moteur PAU",
                "Expérience mémorable, fidélisation accrue",
              ].map((it) => (
                <li key={it} className="flex items-start gap-3">
                  <span className="text-[var(--color-or)] mt-0.5">◆</span>
                  <span className="text-[var(--color-ivoire)]/85">{it}</span>
                </li>
              ))}
            </ul>

            <a href="#contact" className="btn-or inline-flex">
              Demander une démo boutique
              <span aria-hidden>→</span>
            </a>
          </div>
        </div>
      </div>
    </section>
  );
}
