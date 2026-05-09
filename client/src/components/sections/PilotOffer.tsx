/**
 * Maison Couture Nocturne — Pilot offer.
 * Editorial card with pricing terms and exclusivity badge.
 */
const TERMS = [
  {
    k: "Mois 1",
    v: "Premier mois offert",
    d: "Aucun engagement, intégration complète, support concierge.",
  },
  {
    k: "Commission",
    v: "5 %",
    d: "Sur le chiffre d'affaires généré via TRYONYOU. Aucun coût fixe.",
  },
  {
    k: "Paiement",
    v: "à 15 jours",
    d: "Facturation transparente, paiement à 15 jours fin de mois.",
  },
];

export default function PilotOffer() {
  return (
    <section id="pilote" className="relative py-24 md:py-36">
      <div className="container">
        <div className="hairline mb-16 reveal-up" />

        <div className="grid grid-cols-1 lg:grid-cols-12 gap-10">
          <div className="lg:col-span-5 reveal-up">
            <div className="roman mb-6">V</div>
            <span className="eyebrow mb-5 inline-flex">L'offre Pilote</span>
            <h2 className="display-l mb-6">
              Une saison pour
              <br />
              <span className="accent-italic">tout changer.</span>
            </h2>
            <p className="text-[17px] leading-[1.75] text-[var(--color-ivoire)]/80 mb-8 max-w-[44ch]">
              Lancez TRYONYOU sur un périmètre maîtrisé — une catégorie, une boutique
              flagship, votre site e-commerce — et mesurez l'impact sur 90 jours.
              Aucun risque, intégration accompagnée, exclusivité contractuelle pour
              les six premières maisons partenaires.
            </p>
            <a href="#contact" className="btn-or">
              Réserver le pilote
              <span aria-hidden>→</span>
            </a>
          </div>

          <div className="lg:col-span-6 lg:col-start-7 reveal-up" data-delay="180">
            <div className="border border-[rgba(201,168,76,0.35)] p-8 md:p-12 bg-[rgba(26,22,20,0.5)]">
              <div className="flex items-center justify-between mb-8">
                <span className="font-display italic text-[var(--color-or)] text-[26px]">
                  Pilote Maison
                </span>
                <span className="chip">6 places · Saison FW 2026</span>
              </div>
              <div className="space-y-6">
                {TERMS.map((t) => (
                  <div key={t.k} className="grid grid-cols-12 gap-4 pb-6 border-b border-[rgba(201,168,76,0.18)] last:border-b-0 last:pb-0">
                    <div className="col-span-4 md:col-span-3">
                      <div className="text-[10px] tracking-[0.24em] uppercase text-[var(--color-fog)]">
                        {t.k}
                      </div>
                    </div>
                    <div className="col-span-8 md:col-span-9">
                      <div className="font-display text-[var(--color-or)] text-[26px] md:text-[32px] leading-tight mb-2">
                        {t.v}
                      </div>
                      <div className="text-[14px] leading-[1.7] text-[var(--color-ivoire)]/75">
                        {t.d}
                      </div>
                    </div>
                  </div>
                ))}
              </div>

              <div className="mt-10 pt-6 border-t border-[rgba(201,168,76,0.25)] flex items-start gap-3 text-[12px] tracking-[0.04em] text-[var(--color-fog)]">
                <span className="text-[var(--color-or)]">◆</span>
                <span>
                  Inclus&nbsp;: intégration Shopify / API e-commerce, formation
                  équipe, suivi de performance hebdomadaire, exclusivité catégorielle
                  par maison.
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
