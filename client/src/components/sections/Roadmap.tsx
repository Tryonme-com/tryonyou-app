/**
 * TRYONYOU — Roadmap 2026-2028
 * Calendrier stratégique éditorial, asymétrique.
 */
import { useReveal } from "@/hooks/useReveal";

const MILESTONES = [
  {
    year: "2026",
    title: "L'éveil du Miroir",
    items: [
      "Activation de l'IA Personal Shopper v2.0",
      "Déploiement des miroirs AR « Golden Dust »",
      "Pilotes Galeries Lafayette, Sézane, Sandro, Printemps",
    ],
  },
  {
    year: "2027",
    title: "L'expansion Divine",
    items: [
      "Expansion internationale Europe & Asie",
      "Intégration multi-maisons LVMH",
      "Mouvement Divine 2027 — la fin de l'ancien retail",
    ],
  },
  {
    year: "2028",
    title: "L'héritage textile",
    items: [
      "Traçabilité textile par blockchain",
      "Production CAP Just-In-Time à grande échelle",
      "Standardisation du Protocole Zero-Size",
    ],
  },
];

export default function Roadmap() {
  useReveal();

  return (
    <section id="roadmap" className="relative py-28 md:py-36 bg-[var(--color-anthracite)]">
      <div className="container reveal-up">
        <div className="grid grid-cols-12 gap-8 mb-16">
          <div className="col-span-12 md:col-span-5">
            <span className="roman">V</span>
            <div className="mt-3 eyebrow">Roadmap stratégique</div>
            <h2 className="display-l mt-6">
              Trois années.
              <br />
              <span className="accent-italic">Trois actes.</span>
            </h2>
          </div>
          <div className="col-span-12 md:col-span-7 flex items-end">
            <p className="text-base md:text-lg text-[var(--color-fog)] leading-relaxed">
              Du miroir pilote à la standardisation industrielle —
              TRYONYOU devient le système d'intelligence de mode définitif,
              un avantage concurrentiel inexpugnable pour les décennies à venir.
            </p>
          </div>
        </div>

        <div className="hairline mb-12" />

        {/* Timeline asymétrique */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-px bg-[rgba(197,164,109,0.18)]">
          {MILESTONES.map((m, i) => (
            <div
              key={m.year}
              className="bg-[var(--color-noir)] p-8 md:p-10 relative group"
            >
              {/* Numéro de phase */}
              <div className="absolute top-4 right-4 text-[var(--color-or)]/30 font-display italic text-5xl md:text-6xl leading-none">
                0{i + 1}
              </div>

              <div className="font-display italic text-[var(--color-or)] text-3xl md:text-4xl mb-2">
                {m.year}
              </div>
              <h3 className="font-display text-[var(--color-ivoire)] text-xl md:text-2xl mb-6 leading-tight">
                {m.title}
              </h3>

              <ul className="space-y-3">
                {m.items.map((it) => (
                  <li
                    key={it}
                    className="flex items-start gap-3 text-sm text-[var(--color-ivoire)]/85 leading-relaxed"
                  >
                    <span
                      aria-hidden
                      className="mt-2 w-2 h-px bg-[var(--color-or-luxe)] flex-shrink-0"
                    />
                    <span>{it}</span>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
