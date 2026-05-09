/**
 * Maison Couture Nocturne — Hero asymmetric split.
 * Left (cols 1-7): monumental italic headline + lede + CTAs.
 * Right (cols 8-12): full-bleed Gemelo Digital portrait inside mirror-frame.
 */
export default function Hero() {
  return (
    <section id="hero" className="relative pt-28 md:pt-36 pb-20 md:pb-32 overflow-hidden">
      {/* Background flourish */}
      <div
        aria-hidden
        className="pointer-events-none absolute inset-0"
        style={{
          background:
            "radial-gradient(60% 50% at 18% 30%, rgba(201,168,76,0.12) 0%, transparent 70%), radial-gradient(45% 40% at 90% 70%, rgba(201,168,76,0.07) 0%, transparent 70%)",
        }}
      />

      <div className="container relative grid grid-cols-1 lg:grid-cols-12 gap-10 lg:gap-12 items-center">
        <div className="lg:col-span-7 reveal-up">
          <div className="flex items-center gap-4 mb-6">
            <span className="eyebrow">Maison Tech · Paris</span>
            <span className="hidden md:inline text-[11px] tracking-[0.22em] uppercase text-[var(--color-fog)]">
              Brevet PCT/EP2025/067317
            </span>
          </div>

          <h1 className="display-xl mb-8">
            <span className="block">La fin</span>
            <span className="accent-italic block">des retours.</span>
          </h1>

          <p className="max-w-[58ch] text-[17px] md:text-[18px] leading-[1.7] text-[var(--color-ivoire)]/85">
            TRYONYOU offre aux maisons de mode un essayage virtuel de précision&nbsp;:
            jumeau numérique biométrique, ajustement vêtement temps réel et simulation
            textile photoréaliste. Vos clients voient comment la pièce tombe sur leur
            corps réel — avant l'achat. Vos retours s'effondrent.
          </p>

          <div className="mt-10 flex flex-col sm:flex-row gap-4">
            <a href="#contact" className="btn-or">
              Réserver le pilote
              <span aria-hidden>→</span>
            </a>
            <a href="#demo" className="btn-ghost">
              <span>Voir la démo</span>
            </a>
          </div>

          <div className="mt-12 grid grid-cols-3 gap-6 max-w-xl">
            {[
              { v: "−85%", l: "de retours" },
              { v: "+32%", l: "de conversion" },
              { v: "99,7%", l: "de précision" },
            ].map((m) => (
              <div key={m.l}>
                <div className="font-display text-[var(--color-or)] text-[28px] md:text-[34px] leading-none">
                  {m.v}
                </div>
                <div className="mt-2 text-[10px] tracking-[0.22em] uppercase text-[var(--color-fog)]">
                  {m.l}
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="lg:col-span-5 reveal-up" data-delay="180">
          <div className="mirror-frame aspect-[3/4] overflow-hidden">
            <img
              src="/images/gemelo-digital.jpg"
              alt="Jumeau numérique TRYONYOU — gemelo digital biométrique"
              className="w-full h-full object-cover object-top"
              loading="eager"
            />
            <div className="absolute top-4 left-4 right-4 flex items-center justify-between text-[10px] tracking-[0.24em] uppercase text-[var(--color-or)]">
              <span>Gemelo Digital · V11</span>
              <span className="inline-flex items-center gap-2">
                <span className="w-1.5 h-1.5 rounded-full bg-[var(--color-or)] animate-pulse" />
                Live
              </span>
            </div>
            <div className="absolute bottom-5 left-5 right-5 flex items-end justify-between gap-3">
              <div className="text-[11px] tracking-[0.2em] uppercase text-[var(--color-ivoire)]/90">
                Mesh fidelity&nbsp;·&nbsp;<span className="text-[var(--color-or)]">High</span>
              </div>
              <div className="text-[11px] tracking-[0.2em] uppercase text-[var(--color-ivoire)]/90">
                Scan&nbsp;·&nbsp;<span className="text-[var(--color-or)]">Confirmé</span>
              </div>
            </div>
          </div>

          <div className="mt-6 flex flex-wrap gap-2">
            <span className="chip">Jumeau Numérique</span>
            <span className="chip">Simulation Textile</span>
            <span className="chip">Zéro friction</span>
          </div>
        </div>
      </div>

      {/* Trust marquee */}
      <div className="mt-16 md:mt-24 border-y border-[rgba(201,168,76,0.18)] py-5 overflow-hidden">
        <div className="marquee-track">
          {[...Array(2)].map((_, dup) => (
            <div key={dup} className="flex items-center gap-12 px-8 shrink-0">
              {[
                "PCT/EP2025/067317",
                "Jusqu'à 10 000 utilisateurs simultanés",
                "99,7 % de précision biométrique",
                "Jusqu'à −85 % de retours",
                "RGPD · Données chiffrées",
                "Made in Paris",
              ].map((t) => (
                <span
                  key={t + dup}
                  className="text-[12px] tracking-[0.24em] uppercase text-[var(--color-fog)] flex items-center gap-12"
                >
                  {t}
                  <span aria-hidden className="text-[var(--color-or)]">◆</span>
                </span>
              ))}
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
