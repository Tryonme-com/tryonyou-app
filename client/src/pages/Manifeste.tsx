/**
 * TRYONYOU — page /manifeste
 * « TRYONYOU x GALERIES LAFAYETTE : Le Futur de l'Élégance Invisible »
 * Long-form éditorial — 5 chapitres + appel final.
 *
 * Style : asymétrie éditoriale, hairlines or, glassmorphism, Playfair Display italic.
 */
import { useEffect } from "react";
import { Link } from "wouter";
import SiteHeader from "@/components/sections/SiteHeader";
import SiteFooter from "@/components/sections/SiteFooter";
import { useReveal } from "@/hooks/useReveal";

export default function Manifeste() {
  useReveal();

  useEffect(() => {
    window.scrollTo({ top: 0, behavior: "auto" });
    document.title = "Manifeste — TRYONYOU × Galeries Lafayette";
  }, []);

  return (
    <div className="min-h-screen bg-[var(--color-noir)]">
      <SiteHeader />

      {/* HERO */}
      <section className="relative pt-44 md:pt-56 pb-20 md:pb-28 overflow-hidden">
        <div
          aria-hidden
          className="absolute inset-0 pointer-events-none"
          style={{
            background:
              "radial-gradient(ellipse at 50% 10%, rgba(197, 164, 109, 0.14), transparent 60%)",
          }}
        />
        <div className="container reveal-up relative">
          <div className="eyebrow mb-6">Manifeste — Édition Lafayette</div>
          <h1 className="display-xl mb-8 max-w-5xl">
            TRYONYOU × Galeries Lafayette :
            <br />
            <span className="accent-italic">Le Futur de l'Élégance Invisible.</span>
          </h1>
          <p className="text-lg md:text-xl text-[var(--color-fog)] max-w-3xl leading-relaxed">
            Une révolution philosophique de l'ajustement, qui restaure
            l'essence de la Haute Couture au cœur de l'ère digitale.
          </p>

          <div className="mt-12 flex flex-wrap gap-4">
            <Link href="/offre" className="btn-or">
              <span>Découvrir l'Offre Pionnière</span>
            </Link>
            <Link href="/tryon" className="btn-ghost">
              <span>Tester le Miroir</span>
            </Link>
          </div>
        </div>
      </section>

      {/* CHAPITRE I — Le Manifeste de la Certitude */}
      <section className="py-20 md:py-28">
        <div className="container reveal-up">
          <div className="grid grid-cols-12 gap-8 mb-12">
            <div className="col-span-12 md:col-span-3">
              <span className="roman">I</span>
              <div className="mt-3 eyebrow">Le Manifeste</div>
            </div>
            <div className="col-span-12 md:col-span-9">
              <h2 className="display-l mb-6">
                Au-delà du <em className="accent-italic">prêt-à-porter</em>.
              </h2>
              <p className="text-base md:text-lg text-[var(--color-ivoire)]/90 leading-relaxed mb-5">
                Le retail traditionnel s'enfonce dans une crise de pertinence
                structurelle. Le paradigme actuel — fondé sur des normes
                arbitraires et une production de masse déconnectée des
                réalités individuelles — a atteint son point de rupture.
              </p>
              <p className="text-base md:text-lg text-[var(--color-ivoire)]/85 leading-relaxed">
                Pour le prestigieux écosystème de la famille Lafayette,
                TRYONYOU n'est pas un simple outil numérique. C'est une
                révolution philosophique de l'ajustement, qui restaure
                l'essence de la Haute Couture au cœur de l'ère digitale.
              </p>
            </div>
          </div>

          <div className="hairline mb-12" />

          {/* Pull-quote Gemelas */}
          <div className="grid grid-cols-12 gap-8 mb-12">
            <div className="col-span-12 md:col-span-5">
              <div className="eyebrow mb-3">L'absurdité du système</div>
              <h3 className="display-m">
                Le scénario des <em className="accent-italic">Gemelas</em>
              </h3>
            </div>
            <div className="col-span-12 md:col-span-7">
              <p className="text-[var(--color-ivoire)]/90 leading-relaxed mb-4">
                Deux individus physiquement identiques se retrouvent
                prisonniers de labels discordants — l'une en M, l'autre en L,
                selon les caprices des marques. Cette incohérence alimente
                le <em>Purgatoire du Retail</em> : une errance frustrante
                entre cabines d'essayage et files d'attente pour des retours
                massifs représentant 30 à 40 % du volume e-commerce.
              </p>
            </div>
          </div>

          <blockquote className="glass-card p-8 md:p-12 my-10">
            <p className="font-display italic text-2xl md:text-3xl text-[var(--color-or-luxe)] leading-snug">
              « Nadie quiere probarse 500 pantalones. Todos quieren saber
              cuál es el suyo. TRYONYOU vende certeza. »
            </p>
          </blockquote>

          {/* Privacy Firewall */}
          <div className="grid grid-cols-12 gap-8 mt-12">
            <div className="col-span-12 md:col-span-5">
              <div className="eyebrow mb-3">Privacy Firewall</div>
              <h3 className="display-m">
                Un <em className="accent-italic">bouclier d'éthique.</em>
              </h3>
            </div>
            <div className="col-span-12 md:col-span-7">
              <p className="text-[var(--color-ivoire)]/90 leading-relaxed">
                Nous transformons la donnée biométrique en bouclier d'éthique.
                Le client ne voit jamais un chiffre, seulement sa propre
                perfection. Le luxe redéfini non par l'étiquette, mais par
                l'ajustement absolu.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* CHAPITRE II — L'Expérience Omnicanale */}
      <section className="py-20 md:py-28 bg-[var(--color-anthracite)]">
        <div className="container reveal-up">
          <div className="grid grid-cols-12 gap-8 mb-12">
            <div className="col-span-12 md:col-span-3">
              <span className="roman">II</span>
              <div className="mt-3 eyebrow">L'Expérience</div>
            </div>
            <div className="col-span-12 md:col-span-9">
              <h2 className="display-l mb-6">
                Du miroir physique
                <br />
                <span className="accent-italic">à l'app mobile.</span>
              </h2>
              <p className="text-base md:text-lg text-[var(--color-ivoire)]/85 leading-relaxed">
                La fusion du prestige physique et de l'agilité numérique
                est l'impératif stratégique pour capturer les générations Z
                et Alpha. Chaque point de contact devient un podium personnel.
              </p>
            </div>
          </div>

          <div className="hairline mb-12" />

          <div className="grid grid-cols-1 md:grid-cols-3 gap-px bg-[rgba(197,164,109,0.2)]">
            <div className="bg-[var(--color-noir)] p-8 md:p-10">
              <div className="font-display italic text-[var(--color-or)] text-2xl mb-2">
                Séquence Bien Divina
              </div>
              <p className="text-[var(--color-ivoire)]/85 text-sm leading-relaxed mb-4">
                Le smartphone se transforme en passerelle de défilé.
                Sous l'égide du <strong className="text-[var(--color-or-luxe)]">Golden Peacock</strong> —
                représenté par Pau, notre paon en esmoquin — le
                <em> Chasquido de Pau</em> déclenche une métamorphose
                instantanée de l'avatar.
              </p>
              <p className="font-display italic text-[var(--color-or-luxe)] text-sm leading-snug">
                « Yo no sé de marcas ni de números, pero yo sé que estoy
                bien divina. »
              </p>
            </div>

            <div className="bg-[var(--color-noir)] p-8 md:p-10">
              <div className="font-display italic text-[var(--color-or)] text-2xl mb-2">
                Miroir Divineo V7 / V9
              </div>
              <p className="text-[var(--color-ivoire)]/85 text-sm leading-relaxed">
                En magasin, l'apogée — <strong>The Snap</strong>. D'un geste,
                les labels S, M, L se désintègrent visuellement sur le miroir
                en une poussière dorée, laissant place à une recommandation
                exclusive pilotée par l'Agente 70.
              </p>
            </div>

            <div className="bg-[var(--color-noir)] p-8 md:p-10">
              <div className="font-display italic text-[var(--color-or)] text-2xl mb-2">
                Interface Vogue Tech
              </div>
              <p className="text-[var(--color-ivoire)]/85 text-sm leading-relaxed">
                Glassmorphism et palette exclusive : Anthracite{" "}
                <span className="text-[var(--color-or-luxe)]">#141619</span>,
                Or de Luxe <span className="text-[var(--color-or-luxe)]">#C5A46D</span>,
                Beige Clair <span className="text-[var(--color-or-luxe)]">#F5EFE6</span>.
                Sous la simplicité, un moteur d'une puissance inouïe.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* CHAPITRE III — ABVETOS (lien vers la section home) */}
      <section className="py-20 md:py-28">
        <div className="container reveal-up">
          <div className="grid grid-cols-12 gap-8 mb-10">
            <div className="col-span-12 md:col-span-3">
              <span className="roman">III</span>
              <div className="mt-3 eyebrow">Architecture</div>
            </div>
            <div className="col-span-12 md:col-span-9">
              <h2 className="display-l mb-6">
                Le cœur intelligent
                <br />
                <span className="accent-italic">ABVETOS.</span>
              </h2>
              <p className="text-base md:text-lg text-[var(--color-ivoire)]/85 leading-relaxed mb-4">
                Quatre modules — <strong>PAU</strong> (Personal Analytics Unit),
                {" "}<strong>ABVET</strong> (Advanced Biometric Verification),
                {" "}<strong>CAP</strong> (Creative Auto-Production),
                {" "}<strong>FTT</strong> (Fashion Trend Tracker) —
                orchestrés par l'<em className="accent-italic">Agente 70</em>,
                qui supervise cinquante agents intelligents répartis en sept
                blocs fonctionnels.
              </p>
              <p className="text-base md:text-lg text-[var(--color-fog)] leading-relaxed">
                Propulsé par React 18.3.1 et Vite 7.1.2 : temps de chargement
                inférieur à 1,5 s, score Lighthouse 95+. Une fluidité de grade luxe.
              </p>
              <div className="mt-8">
                <a href="/#abvetos" className="btn-ghost">
                  <span>Voir le détail des modules</span>
                </a>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* CHAPITRE IV — IP */}
      <section className="py-20 md:py-28 bg-[var(--color-anthracite)]">
        <div className="container reveal-up">
          <div className="grid grid-cols-12 gap-8 mb-10">
            <div className="col-span-12 md:col-span-3">
              <span className="roman">IV</span>
              <div className="mt-3 eyebrow">Forteresse IP</div>
            </div>
            <div className="col-span-12 md:col-span-9">
              <h2 className="display-l mb-6">
                Protection du patrimoine
                <br />
                <span className="accent-italic">& valeur des actifs.</span>
              </h2>
              <p className="text-base md:text-lg text-[var(--color-ivoire)]/85 leading-relaxed mb-6">
                L'innovation est verrouillée par la patente
                {" "}<strong className="text-[var(--color-or)]">PCT/EP2025/067317</strong>.
                Huit Super-Claims, vingt-deux revendications. Huit marques
                déposées — ABVETOS®, ULTRA-PLUS-ULTIMATUM®, Golden Peacock® et
                au-delà — protègent notre écosystème.
              </p>
              <p className="text-base md:text-lg text-[var(--color-fog)] leading-relaxed">
                Valeur actuelle du portefeuille IP estimée entre
                {" "}<strong className="text-[var(--color-or-luxe)]">120 M€ et 400 M€</strong>.
                Un actif immatériel majeur pour le groupe.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* CHAPITRE V — Impact stratégique */}
      <section className="py-20 md:py-28">
        <div className="container reveal-up">
          <div className="grid grid-cols-12 gap-8 mb-10">
            <div className="col-span-12 md:col-span-3">
              <span className="roman">V</span>
              <div className="mt-3 eyebrow">Impact 2025—2028</div>
            </div>
            <div className="col-span-12 md:col-span-9">
              <h2 className="display-l mb-6">
                Le catalyseur de la
                <br />
                <span className="accent-italic">rentabilité future.</span>
              </h2>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-px bg-[rgba(197,164,109,0.2)] mt-8">
                <div className="bg-[var(--color-noir)] p-8">
                  <div className="text-[var(--color-or)] font-display text-4xl md:text-5xl mb-2">— 85%</div>
                  <div className="text-[11px] tracking-[0.22em] uppercase text-[var(--color-fog)] mb-3">
                    Taux de retour
                  </div>
                  <p className="text-sm text-[var(--color-ivoire)]/80">
                    Réduction massive des retours et donc des coûts logistiques.
                  </p>
                </div>
                <div className="bg-[var(--color-noir)] p-8">
                  <div className="text-[var(--color-or)] font-display text-4xl md:text-5xl mb-2">— 60%</div>
                  <div className="text-[11px] tracking-[0.22em] uppercase text-[var(--color-fog)] mb-3">
                    Gaspillage d'inventaire
                  </div>
                  <p className="text-sm text-[var(--color-ivoire)]/80">
                    Augmentation directe de la marge nette et de la valorisation.
                  </p>
                </div>
                <div className="bg-[var(--color-noir)] p-8">
                  <div className="text-[var(--color-or)] font-display text-4xl md:text-5xl mb-2">+ 40%</div>
                  <div className="text-[11px] tracking-[0.22em] uppercase text-[var(--color-fog)] mb-3">
                    Satisfaction client
                  </div>
                  <p className="text-sm text-[var(--color-ivoire)]/80">
                    L'acheteur occasionnel devient ambassadeur fidèle.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* CONCLUSION */}
      <section className="py-24 md:py-32 bg-[var(--color-anthracite)]">
        <div className="container reveal-up">
          <div className="max-w-4xl mx-auto text-center">
            <div className="eyebrow justify-center mb-6">En conclusion</div>
            <h2 className="display-l mb-8">
              TRYONYOU ne vend pas des vêtements.
              <br />
              <span className="accent-italic">Il vend la certitude d'être « bien divina ».</span>
            </h2>
            <p className="text-base md:text-lg text-[var(--color-ivoire)]/85 leading-relaxed mb-10">
              Libéré de la tyrannie des chiffres. Pour les Galeries Lafayette,
              il s'agit du système d'intelligence de mode définitif — un avantage
              concurrentiel inexpugnable pour les décennies à venir.
            </p>
            <div className="flex flex-wrap gap-4 justify-center">
              <Link href="/offre" className="btn-or">
                <span>Activer l'Offre Pionnière</span>
              </Link>
              <a href="/#contact" className="btn-ghost">
                <span>Engager un dialogue</span>
              </a>
            </div>
          </div>
        </div>
      </section>

      <SiteFooter />
    </div>
  );
}
