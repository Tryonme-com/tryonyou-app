/**
 * TRYONYOU — ZeroSizeProtocol
 * Le scénario des "Gemelas" et l'éradication des étiquettes S/M/L.
 * Style : asymétrique, hairlines or, glassmorphism subtil.
 */
import { useReveal } from "@/hooks/useReveal";

export default function ZeroSizeProtocol() {
  useReveal();

  return (
    <section id="zero-size" className="relative py-28 md:py-36 overflow-hidden">
      {/* Background subtil */}
      <div
        aria-hidden
        className="absolute inset-0 pointer-events-none"
        style={{
          background:
            "radial-gradient(ellipse at 20% 30%, rgba(197, 164, 109, 0.07), transparent 55%), radial-gradient(ellipse at 80% 70%, rgba(197, 164, 109, 0.05), transparent 55%)",
        }}
      />

      <div className="container reveal-up relative">
        {/* En-tête asymétrique */}
        <div className="grid grid-cols-12 gap-8 mb-16">
          <div className="col-span-12 md:col-span-5">
            <span className="roman">II</span>
            <div className="mt-3 eyebrow">Le Protocole Zero-Size</div>
          </div>
          <div className="col-span-12 md:col-span-7">
            <h2 className="display-l mb-6">
              L'éradication des étiquettes au profit de
              <span className="accent-italic"> l'émotion et de la précision biométrique.</span>
            </h2>
            <p className="text-base md:text-lg text-[var(--color-fog)] leading-relaxed max-w-xl">
              Nous ne vendons pas des vêtements. Nous vendons la certitude.
              Notre Privacy Firewall transforme la donnée biométrique en bouclier
              d'éthique : le client ne voit jamais un chiffre, seulement sa propre perfection.
            </p>
          </div>
        </div>

        <div className="hairline mb-16" />

        {/* Le canon commercial — Les Gemelas */}
        <div className="grid grid-cols-12 gap-8 md:gap-12">
          <div className="col-span-12 md:col-span-7 glass-card p-8 md:p-12">
            <div className="eyebrow mb-6">Le Canon Commercial</div>
            <h3 className="display-m mb-6">
              Le scénario des <em className="accent-italic">Gemelas</em>
            </h3>
            <p className="text-[var(--color-ivoire)]/85 leading-relaxed mb-4">
              Deux individus physiquement identiques. Pourtant prisonniers
              de labels discordants : l'une en M, l'autre en L, selon les caprices
              des marques. Cette incohérence alimente le <em>Purgatoire du Retail</em>
              {" "}— une errance frustrante entre cabines d'essayage et files
              d'attente pour des retours massifs.
            </p>
            <p className="text-[var(--color-or-luxe)] font-display italic text-xl md:text-2xl mt-8 leading-tight">
              « Nadie quiere probarse 500 pantalones. Todos quieren saber
              cuál es el suyo. TRYONYOU vende certeza. »
            </p>
          </div>

          <div className="col-span-12 md:col-span-5 flex flex-col gap-6">
            <div className="border border-[rgba(197,164,109,0.25)] p-8">
              <div className="text-[var(--color-or)] font-display text-4xl md:text-5xl mb-2">30—40%</div>
              <div className="text-[11px] tracking-[0.22em] uppercase text-[var(--color-fog)]">
                Volume e-commerce en retours
              </div>
            </div>
            <div className="border border-[rgba(197,164,109,0.25)] p-8">
              <div className="text-[var(--color-or)] font-display text-4xl md:text-5xl mb-2">— 85%</div>
              <div className="text-[11px] tracking-[0.22em] uppercase text-[var(--color-fog)]">
                Taux de retour avec TRYONYOU
              </div>
            </div>
            <div className="border border-[rgba(197,164,109,0.25)] p-8">
              <div className="text-[var(--color-or)] font-display text-4xl md:text-5xl mb-2">+ 40%</div>
              <div className="text-[11px] tracking-[0.22em] uppercase text-[var(--color-fog)]">
                Satisfaction client
              </div>
            </div>
          </div>
        </div>

        {/* Élégance Invisible */}
        <div className="mt-20 max-w-3xl">
          <div className="eyebrow mb-4">L'Élégance Invisible</div>
          <p className="display-m text-[var(--color-ivoire)] leading-tight">
            Nous instaurons une <em className="accent-italic">Logique d'Élégance</em>
            {" "}qui ignore les centimètres bruts pour se concentrer sur le tombé
            architectural et la sensation de seconde peau.
          </p>
        </div>
      </div>
    </section>
  );
}
