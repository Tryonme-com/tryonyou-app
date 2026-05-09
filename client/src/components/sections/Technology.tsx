/**
 * Maison Couture Nocturne — Technology section.
 * Patent + tech stack chips, asymmetric col 1-4 vs 6-12.
 */
const MODULES = [
  {
    code: "PAU V11",
    name: "Personal Avatar Unit",
    body: "Moteur d'avatar 3D photoréaliste, drapé textile et expression émotionnelle. Rendu Three.js avec matériaux MeshStandard luxury.",
  },
  {
    code: "DIVINEO",
    name: "Skeleton Mapping",
    body: "Mapping temps réel MediaPipe → Kalidokit → squelette 3D Three.js. 33 points clés, précision 99,7 %.",
  },
  {
    code: "EBTT",
    name: "Elastic Body-Textile Transform",
    body: "Calcul d'ajustement élastique vêtement-corps : scaleX, scaleY, scores de fit, sélection automatique du meilleur ajustement.",
  },
  {
    code: "CAP",
    name: "Cloth Animation Pipeline",
    body: "Simulation textile photoréaliste, drapé physique, comportement matière (coton, soie, cachemire, denim).",
  },
];

export default function Technology() {
  return (
    <section id="technologie" className="relative py-24 md:py-36">
      <div className="container">
        <div className="hairline mb-16 reveal-up" />

        <div className="grid grid-cols-1 lg:grid-cols-12 gap-10 mb-16">
          <div className="lg:col-span-4 reveal-up">
            <div className="roman mb-6">IV</div>
            <span className="eyebrow mb-5 inline-flex">Technologie</span>
            <h2 className="display-l">
              Une architecture
              <br />
              <span className="accent-italic">brevetée.</span>
            </h2>
          </div>

          <div className="lg:col-span-7 lg:col-start-6 lg:pt-6 reveal-up" data-delay="160">
            <p className="text-[17px] leading-[1.75] text-[var(--color-ivoire)]/85 mb-6">
              TRYONYOU repose sur un protocole propriétaire déposé à l'Office Européen
              des Brevets. L'ensemble — moteur d'avatar, mapping squelette, transform
              élastique, simulation textile — est conçu pour le retail enterprise&nbsp;:
              fiabilité production, scalabilité 10 000 utilisateurs simultanés,
              chiffrement bout en bout.
            </p>

            <div className="flex flex-wrap items-center gap-3 mb-10">
              <span className="chip">Brevet PCT/EP2025/067317</span>
              <span className="chip">RGPD &amp; Données chiffrées</span>
              <span className="chip">Cloud souverain</span>
              <span className="chip">SDK Web · iOS · Android</span>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-px bg-[rgba(201,168,76,0.18)]">
          {MODULES.map((m, i) => (
            <article
              key={m.code}
              className="bg-[var(--color-noir)] p-8 md:p-10 reveal-up"
              data-delay={i * 120}
            >
              <div className="flex items-baseline justify-between mb-4 gap-4">
                <span className="font-display italic text-[var(--color-or)] text-[24px] md:text-[28px]">
                  {m.name}
                </span>
                <span className="text-[10px] tracking-[0.28em] uppercase text-[var(--color-fog)]">
                  [{m.code}]
                </span>
              </div>
              <div className="hairline mb-5" />
              <p className="text-[15px] leading-[1.7] text-[var(--color-ivoire)]/80">{m.body}</p>
            </article>
          ))}
        </div>

        {/* Tech stack credits */}
        <div className="mt-12 flex flex-wrap items-center justify-between gap-6 text-[11px] tracking-[0.22em] uppercase text-[var(--color-fog)]">
          <span>Stack&nbsp;·&nbsp;Three.js · MediaPipe · Kalidokit · React · Vite</span>
          <span>Conçu &amp; assemblé à Paris</span>
        </div>
      </div>
    </section>
  );
}
