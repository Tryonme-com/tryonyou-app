/**
 * Maison Couture Nocturne — Problem section.
 * Editorial split: Roman numeral I + heading on left col 1-5; lede on right col 7-12.
 * Image "Retour & Échange" mounted asymmetrically below.
 */
export default function Problem() {
  return (
    <section id="probleme" className="relative py-24 md:py-36">
      <div className="container">
        <div className="hairline mb-16 reveal-up" />

        <div className="grid grid-cols-1 lg:grid-cols-12 gap-10 lg:gap-16">
          <div className="lg:col-span-5 reveal-up">
            <div className="roman mb-6">I</div>
            <span className="eyebrow mb-5 inline-flex">Le problème</span>
            <h2 className="display-l">
              30 % des achats mode <br />
              <span className="accent-italic">reviennent</span> en magasin.
            </h2>
          </div>

          <div className="lg:col-span-7 lg:col-start-7 lg:pt-16 reveal-up" data-delay="160">
            <p className="text-[18px] md:text-[19px] leading-[1.75] text-[var(--color-ivoire)]/85">
              Chaque retour érode la marge, alourdit la logistique et fragilise la
              confiance du client. Les grilles génériques ne suffisent plus&nbsp;:
              elles ignorent la morphologie réelle, la coupe spécifique de chaque
              pièce et le ressenti du tissu. Le client doute, hésite, commande deux
              références — et renvoie au moins l'une d'elles.
            </p>
            <p className="mt-6 text-[18px] md:text-[19px] leading-[1.75] text-[var(--color-ivoire)]/85">
              <span className="accent-italic">TRYONYOU remplace cette incertitude</span> par
              une certitude individuelle, calculée sur le corps réel du client et
              projetée sur le vêtement réel de votre catalogue.
            </p>

            <div className="mt-10 grid grid-cols-1 sm:grid-cols-3 gap-6">
              {[
                { v: "30%", l: "Taux moyen de retours mode en ligne" },
                { v: "12,5 €", l: "Coût logistique moyen d'un retour" },
                { v: "−4 pts", l: "Marge brute érodée chaque saison" },
              ].map((m) => (
                <div key={m.l} className="border-t border-[rgba(201,168,76,0.25)] pt-5">
                  <div className="font-display text-[var(--color-or)] text-[34px] leading-none">
                    {m.v}
                  </div>
                  <div className="mt-3 text-[12px] tracking-[0.18em] uppercase text-[var(--color-fog)] leading-snug">
                    {m.l}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Image asymmetric */}
        <div className="mt-20 grid grid-cols-1 lg:grid-cols-12 gap-10 items-end">
          <div className="lg:col-span-7 lg:col-start-2 reveal-up">
            <div className="mirror-frame overflow-hidden" style={{ aspectRatio: '4/5' }}>
              <img
                src="/images/retour-echange.jpg"
                alt="File d'attente au comptoir Retour & Échange — symptôme du fit incertain"
                className="w-full h-full object-contain"
                style={{ background: 'var(--color-noir)' }}
                loading="lazy"
              />
            </div>
          </div>
          <div className="lg:col-span-3 reveal-up" data-delay="160">
            <p className="font-display italic text-[var(--color-or)] text-[20px] leading-[1.4]">
              « Le retour n'est pas un service —
              <br />
              c'est une promesse non tenue. »
            </p>
            <p className="mt-3 text-[11px] tracking-[0.22em] uppercase text-[var(--color-fog)]">
              Observation terrain&nbsp;·&nbsp;Paris
            </p>
          </div>
        </div>
      </div>
    </section>
  );
}
