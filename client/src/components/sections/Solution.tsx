/**
 * Maison Couture Nocturne — Solution section.
 * Three steps in roman numerals with editorial vertical rhythm.
 */
const STEPS = [
  {
    num: "I",
    title: "Le client crée son profil corporel",
    body: "À partir de quelques images guidées, TRYONYOU compose un profil morphologique chiffré, sans aucune mesure traditionnelle. La donnée est anonymisée et chiffrée.",
    chip: "Scan biométrique A4",
  },
  {
    num: "II",
    title: "TRYONYOU génère le jumeau numérique",
    body: "Le moteur PAU V11 transforme le profil en avatar 3D photoréaliste, paramétré pour la simulation de coupe, le drapé et le rendu textile temps réel.",
    chip: "Moteur PAU V11",
  },
  {
    num: "III",
    title: "La maison montre l'ajustement parfait",
    body: "Le vêtement réel du catalogue est projeté sur le jumeau. Le client voit la coupe, le drapé, l'aisance — la décision d'achat devient évidente.",
    chip: "Miroir Digital",
  },
];

export default function Solution() {
  return (
    <section id="solution" className="relative py-24 md:py-36 bg-[var(--color-graphite)]">
      <div className="container">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-10 mb-16">
          <div className="lg:col-span-5 reveal-up">
            <span className="eyebrow mb-5 inline-flex">La solution</span>
            <h2 className="display-l">
              Trois actes,
              <br />
              <span className="accent-italic">une seule certitude.</span>
            </h2>
          </div>
          <div className="lg:col-span-6 lg:col-start-7 lg:pt-6 reveal-up" data-delay="140">
            <p className="text-[17px] leading-[1.75] text-[var(--color-ivoire)]/80">
              Ce n'est pas un avatar décoratif, c'est un moteur de décision. TRYONYOU
              s'intègre dans la fiche produit comme un essayage en cabine — fluide, sûr,
              élégant — et déclenche le passage en checkout avec une confiance inédite.
            </p>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-px bg-[rgba(201,168,76,0.2)]">
          {STEPS.map((s, i) => (
            <div
              key={s.num}
              className="bg-[var(--color-graphite)] p-8 md:p-10 reveal-up"
              data-delay={i * 160}
            >
              <div className="flex items-start justify-between mb-8">
                <span className="roman">{s.num}</span>
                <span className="chip">{s.chip}</span>
              </div>
              <h3 className="display-m mb-4 text-[var(--color-ivoire)]">{s.title}</h3>
              <p className="text-[15px] leading-[1.7] text-[var(--color-ivoire)]/75">{s.body}</p>
              <div className="mt-8 hairline" />
            </div>
          ))}
        </div>

        <div className="mt-20 grid grid-cols-1 lg:grid-cols-12 gap-10 items-center">
          <div className="lg:col-span-6 reveal-up">
            <div className="mirror-frame aspect-[4/5] overflow-hidden">
              <img
                src="/images/mirror-smart.jpg"
                alt="Miroir intelligent TRYONYOU en boutique — sélection parfaite"
                className="w-full h-full object-cover"
                loading="lazy"
              />
            </div>
          </div>
          <div className="lg:col-span-5 lg:col-start-8 reveal-up" data-delay="180">
            <span className="eyebrow mb-5 inline-flex">Le miroir intelligent</span>
            <h3 className="display-l mb-6">
              Une cabine
              <br />
              <span className="accent-italic">augmentée.</span>
            </h3>
            <p className="text-[17px] leading-[1.75] text-[var(--color-ivoire)]/80 mb-8">
              Le miroir TRYONYOU détecte la silhouette dès l'entrée en cabine,
              charge la sélection personnalisée et propose les combinaisons —
              vêtements, accessoires, looks complets. Le vendeur reçoit la commande
              en temps réel, le client repart avec la pièce parfaite.
            </p>
            <ul className="space-y-3 text-[14px]">
              {[
                "Ma sélection parfaite — 5 pièces générées sur le profil",
                "Réservation cabine instantanée par QR sécurisé",
                "Combinaisons recommandées par le moteur PAU",
                "Silhouette enregistrée sous protocole chiffré",
              ].map((it) => (
                <li key={it} className="flex items-start gap-3">
                  <span className="text-[var(--color-or)] mt-1">◆</span>
                  <span className="text-[var(--color-ivoire)]/85">{it}</span>
                </li>
              ))}
            </ul>
          </div>
        </div>
      </div>
    </section>
  );
}
