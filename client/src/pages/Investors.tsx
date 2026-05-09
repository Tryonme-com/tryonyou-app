/**
 * TRYONYOU — /investors
 *
 * Editorial pitch page: thesis, traction, IP, go-to-market, ask, contact.
 * Style: Maison Couture Nocturne — gold-on-graphite, asymmetric editorial.
 */

import { Link } from "wouter";
import SiteHeader from "@/components/sections/SiteHeader";
import SiteFooter from "@/components/sections/SiteFooter";

export default function Investors() {
  return (
    <div className="min-h-screen flex flex-col bg-[var(--color-noir)]">
      <SiteHeader />

      <main className="flex-1 pt-32 pb-24">
        {/* Hero */}
        <section className="container pb-20">
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-10">
            <div className="lg:col-span-7">
              <span className="eyebrow mb-5 inline-flex">Investors · 2026</span>
              <h1 className="display-l mb-6">
                La fin des retours.
                <br />
                <span className="accent-italic">Le début d'une marge.</span>
              </h1>
              <p className="text-[17px] leading-[1.75] text-[var(--color-ivoire)]/80 max-w-2xl">
                Le retour produit est devenu le centre de coût caché de la mode
                en ligne. TRYONYOU élimine la cause racine — l'incertitude
                d'ajustement — par une projection biométrique brevetée,
                réconciliant l'expérience digitale avec la cabine d'essayage.
              </p>
            </div>

            <div className="lg:col-span-4 lg:col-start-9">
              <div className="border-t border-[var(--color-or)]/30 pt-3">
                <div className="text-[10px] tracking-[0.24em] uppercase text-[var(--color-or)]/70 mb-3">
                  Brevet
                </div>
                <div className="font-display text-[var(--color-ivoire)] text-[22px] leading-tight">
                  PCT/EP2025/067317
                </div>
                <p className="text-[12px] text-white/50 mt-3">
                  Système de projection biométrique pour ajustement vestimentaire,
                  déposé auprès de l'OEB. Couvre la chaîne PAU → CAP → drapé.
                </p>
              </div>
            </div>
          </div>
        </section>

        {/* Thesis pillars */}
        <section className="container pb-20">
          <div className="hairline mb-10" />
          <div className="grid grid-cols-1 md:grid-cols-3 gap-px bg-[rgba(201,168,76,0.2)]">
            {[
              {
                k: "I.",
                title: "Cause racine",
                body: "30 % des achats mode en ligne sont retournés ; 80 % pour cause d'ajustement. Aucune solution actuelle ne résout la cause — elles compensent par la logistique.",
              },
              {
                k: "II.",
                title: "Verrou IP",
                body: "Brevet PCT couvrant la chaîne biométrique → simulation tissu → projection AR. Six maisons partenaires, soixante pièces déjà modélisées.",
              },
              {
                k: "III.",
                title: "Marge nette",
                body: "Réduction des retours de 60 % en pilote. Bascule logistique → marge directe. Modèle SaaS + commission, scalable par marque et par boutique.",
              },
            ].map((p) => (
              <div key={p.k} className="bg-[var(--color-graphite)] p-10">
                <div className="font-display italic text-[var(--color-or)]/70 text-[26px] mb-3">
                  {p.k}
                </div>
                <h3 className="font-display text-[22px] text-[var(--color-ivoire)] mb-4 leading-tight">
                  {p.title}
                </h3>
                <p className="text-[14px] text-white/65 leading-[1.7]">{p.body}</p>
              </div>
            ))}
          </div>
        </section>

        {/* Traction grid */}
        <section className="container pb-20">
          <div className="hairline mb-10" />
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-10">
            <div className="lg:col-span-5">
              <span className="eyebrow mb-5 inline-flex">Traction</span>
              <h2 className="display-l">
                Des chiffres,
                <br />
                <span className="accent-italic">pas des promesses.</span>
              </h2>
            </div>
            <div className="lg:col-span-7">
              <div className="grid grid-cols-2 gap-x-10 gap-y-8">
                {[
                  ["6", "Maisons partenaires"],
                  ["60", "Pièces modélisées"],
                  ["55", "Tissus techniques"],
                  ["−60 %", "Retours en pilote"],
                  ["+18 pts", "Taux de conversion"],
                  ["1", "Brevet PCT déposé"],
                ].map(([v, l]) => (
                  <div key={l} className="border-t border-[var(--color-or)]/30 pt-3">
                    <div className="font-display text-[var(--color-or)] text-[40px] leading-none">
                      {v}
                    </div>
                    <div className="text-[10px] tracking-[0.24em] uppercase text-white/40 mt-3">
                      {l}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </section>

        {/* Use of funds */}
        <section className="container pb-20">
          <div className="hairline mb-10" />
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-10">
            <div className="lg:col-span-5">
              <span className="eyebrow mb-5 inline-flex">Tour de table · Seed</span>
              <h2 className="display-l">
                3 M €
                <br />
                <span className="accent-italic">sur 18 mois.</span>
              </h2>
              <p className="text-[15px] leading-[1.75] text-white/70 mt-6 max-w-md">
                Industrialisation du moteur PAU V11, déploiement en magasin
                pilote (Lafayette, Sézane, Sandro), recrutement R&D, expansion
                des capsules biométriques.
              </p>
            </div>
            <div className="lg:col-span-7">
              <ul className="space-y-px bg-[rgba(201,168,76,0.2)]">
                {[
                  ["40 %", "R&D · moteur PAU + simulation tissu"],
                  ["25 %", "Déploiement boutique · miroir intelligent"],
                  ["20 %", "Expansion catalogue · maisons partenaires"],
                  ["10 %", "Marketing éditorial · marché LFW/PFW"],
                  ["5 %",  "Légal · extension brevet international"],
                ].map(([pct, label]) => (
                  <li
                    key={label}
                    className="bg-[var(--color-graphite)] flex items-baseline justify-between p-5"
                  >
                    <span className="font-display text-[var(--color-or)] text-[24px] w-20">
                      {pct}
                    </span>
                    <span className="text-[14px] text-white/75 flex-1">{label}</span>
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </section>

        {/* Contact CTA */}
        <section className="container">
          <div className="hairline mb-10" />
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-10 items-end">
            <div className="lg:col-span-7">
              <span className="eyebrow mb-5 inline-flex">Contact investisseurs</span>
              <h2 className="display-l">
                Une diligence
                <br />
                <span className="accent-italic">en huit jours.</span>
              </h2>
              <p className="text-[15px] leading-[1.75] text-white/70 mt-6 max-w-xl">
                Memorandum d'investissement, démonstration en boutique,
                accès au backend des pilotes. Réservé aux fonds spécialisés
                tech-luxury & retail tech.
              </p>
            </div>
            <div className="lg:col-span-4 lg:col-start-9">
              <Link href="/#contact" className="btn-or inline-flex">
                Demander le memo
                <span aria-hidden>→</span>
              </Link>
              <p className="text-[11px] tracking-[0.22em] uppercase text-white/40 mt-4">
                investisseurs@tryonyou.app
              </p>
            </div>
          </div>
        </section>
      </main>

      <SiteFooter />
    </div>
  );
}
