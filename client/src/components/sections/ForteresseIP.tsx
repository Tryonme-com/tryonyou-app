/**
 * TRYONYOU — ForteresseIP
 * Brevet PCT/EP2025/067317 + 8 super-claims + 8 marques déposées + valorisation IP.
 */
import { useReveal } from "@/hooks/useReveal";

const SUPER_CLAIMS = [
  {
    title: "Context Engineering Layer",
    desc: "Analyse fine du contexte d'usage et adaptation comportementale.",
  },
  {
    title: "Adaptive Avatar Generation",
    desc: "Génération dynamique d'avatars personnalisés en temps réel.",
  },
  {
    title: "Fabric Fit Comparator",
    desc: "Simulation physique des textiles et du tombé exact.",
  },
  {
    title: "Privacy Firewall",
    desc: "Protection et anonymisation totale de la donnée biométrique.",
  },
  {
    title: "Just-In-Time Production",
    desc: "Réalisation à la commande, sans inventaire dormant.",
  },
  {
    title: "Biometric Payment Verification",
    desc: "Authentification iris et voix, friction zéro.",
  },
  {
    title: "Trend Anticipation Engine",
    desc: "Prédiction des flux de demande mondiaux.",
  },
  {
    title: "AI Stylist Orchestration",
    desc: "Coordination des 50 agents intelligents par l'Agente 70.",
  },
];

const TRADEMARKS = [
  "ABVETOS®",
  "ULTRA-PLUS-ULTIMATUM®",
  "Golden Peacock®",
  "TRYONYOU®",
  "DIVINEO®",
  "PAU®",
  "BIEN DIVINA®",
  "GOLDEN DUST®",
];

export default function ForteresseIP() {
  useReveal();

  return (
    <section id="forteresse-ip" className="relative py-28 md:py-36 overflow-hidden">
      {/* Background : voile or */}
      <div
        aria-hidden
        className="absolute inset-0 pointer-events-none"
        style={{
          background:
            "radial-gradient(ellipse at 50% 0%, rgba(197, 164, 109, 0.10), transparent 60%)",
        }}
      />

      <div className="container reveal-up relative">
        {/* En-tête */}
        <div className="grid grid-cols-12 gap-8 mb-14">
          <div className="col-span-12 md:col-span-5">
            <span className="roman">IV</span>
            <div className="mt-3 eyebrow">Forteresse IP</div>
            <h2 className="display-l mt-6">
              Protection du patrimoine
              <br />
              <span className="accent-italic">& valeur des actifs.</span>
            </h2>
          </div>
          <div className="col-span-12 md:col-span-7 flex items-end">
            <p className="text-base md:text-lg text-[var(--color-fog)] leading-relaxed">
              La sécurisation de nos secrets industriels constitue le socle
              de la valorisation. Nous avons érigé une véritable
              <span className="text-[var(--color-or-luxe)]"> forteresse</span> autour
              de la technologie, des marques et de l'expérience utilisateur.
            </p>
          </div>
        </div>

        {/* Brevet — bandeau premium */}
        <div className="glass-card p-8 md:p-12 mb-14">
          <div className="grid grid-cols-12 gap-8 items-center">
            <div className="col-span-12 md:col-span-7">
              <div className="eyebrow mb-3">Le brevet socle</div>
              <h3 className="display-m text-[var(--color-or)] mb-3">
                PCT / EP2025 / 067317
              </h3>
              <p className="text-[var(--color-ivoire)]/85 text-sm leading-relaxed">
                Huit Super-Claims stratégiques verrouillent l'innovation.
                Chacun est un verrou : impossible de reproduire l'expérience
                TRYONYOU sans franchir la barrière de propriété intellectuelle.
              </p>
            </div>
            <div className="col-span-12 md:col-span-5 grid grid-cols-2 gap-4">
              <div className="border border-[rgba(197,164,109,0.3)] p-5 text-center">
                <div className="font-display text-3xl md:text-4xl text-[var(--color-or)]">8</div>
                <div className="text-[10px] tracking-[0.22em] uppercase text-[var(--color-fog)] mt-1">
                  Super-Claims
                </div>
              </div>
              <div className="border border-[rgba(197,164,109,0.3)] p-5 text-center">
                <div className="font-display text-3xl md:text-4xl text-[var(--color-or)]">22</div>
                <div className="text-[10px] tracking-[0.22em] uppercase text-[var(--color-fog)] mt-1">
                  Revendications
                </div>
              </div>
              <div className="border border-[rgba(197,164,109,0.3)] p-5 text-center">
                <div className="font-display text-3xl md:text-4xl text-[var(--color-or)]">8</div>
                <div className="text-[10px] tracking-[0.22em] uppercase text-[var(--color-fog)] mt-1">
                  Marques déposées
                </div>
              </div>
              <div className="border border-[rgba(197,164,109,0.3)] p-5 text-center">
                <div className="font-display text-2xl md:text-3xl text-[var(--color-or)]">
                  120—400 M€
                </div>
                <div className="text-[10px] tracking-[0.22em] uppercase text-[var(--color-fog)] mt-1">
                  Valorisation IP
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Grille des 8 super-claims */}
        <div className="mb-16">
          <div className="eyebrow mb-6">Les huit Super-Claims</div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-px bg-[rgba(197,164,109,0.18)]">
            {SUPER_CLAIMS.map((c, i) => (
              <div
                key={c.title}
                className="bg-[var(--color-noir)] p-6 md:p-7 hover:bg-[var(--color-graphite)] transition-colors duration-500"
              >
                <div className="font-display italic text-[var(--color-or)] text-2xl mb-3">
                  {String(i + 1).padStart(2, "0")}
                </div>
                <h4 className="font-display text-[var(--color-ivoire)] text-lg mb-2 leading-tight">
                  {c.title}
                </h4>
                <p className="text-[var(--color-fog)] text-sm leading-relaxed">
                  {c.desc}
                </p>
              </div>
            ))}
          </div>
        </div>

        {/* Marques déposées — marquee */}
        <div>
          <div className="eyebrow mb-6">Identité & Marques</div>
          <div className="border-y border-[rgba(197,164,109,0.25)] py-8 overflow-hidden">
            <div className="marquee-track">
              {[...TRADEMARKS, ...TRADEMARKS].map((t, i) => (
                <span
                  key={`${t}-${i}`}
                  className="font-display italic text-2xl md:text-3xl text-[var(--color-or-luxe)] mx-10 whitespace-nowrap"
                >
                  {t}
                </span>
              ))}
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
