/**
 * TRYONYOU — AbvetosArchitecture
 * Les 4 modules core (PAU, ABVET, CAP, FTT) + l'Agente 70.
 * Style : table éditoriale + glassmorphism, stack tech en chiffres.
 */
import { useReveal } from "@/hooks/useReveal";

type ModuleRow = {
  code: string;
  long: string;
  role: string;
  value: string;
};

const MODULES: ModuleRow[] = [
  {
    code: "PAU",
    long: "Personal Analytics Unit",
    role: "Intelligence émotionnelle & IA styliste",
    value: "Recommandations basées sur l'énergie. Fidélisation émotionnelle accrue.",
  },
  {
    code: "ABVET",
    long: "Advanced Biometric Verification",
    role: "Paiement par iris et voix",
    value: "Sécurisation totale. Réduction de la friction transactionnelle.",
  },
  {
    code: "CAP",
    long: "Creative Auto-Production",
    role: "Production Just-In-Time",
    value: "Zero-Stock Luxury Realization. Élimination des invendus.",
  },
  {
    code: "FTT",
    long: "Fashion Trend Tracker",
    role: "Suivi des tendances temps réel",
    value: "Anticipation ultra-précise des flux de demande mondiaux.",
  },
];

const AGENTS = [
  "Deployment & Production",
  "Style & Modulation",
  "Business & Strategy",
  "External Automation",
  "Video & Visual",
  "Live It — Style & Collection",
  "Private Management",
];

export default function AbvetosArchitecture() {
  useReveal();

  return (
    <section id="abvetos" className="relative py-28 md:py-36 bg-[var(--color-anthracite)]">
      <div className="container reveal-up">
        {/* En-tête */}
        <div className="grid grid-cols-12 gap-8 mb-14">
          <div className="col-span-12 md:col-span-4">
            <span className="roman">III</span>
            <div className="mt-3 eyebrow">Architecture ABVETOS</div>
          </div>
          <div className="col-span-12 md:col-span-8">
            <h2 className="display-l mb-5">
              Le cœur intelligent.
              <br />
              <span className="accent-italic">Quatre modules, une orchestration.</span>
            </h2>
            <p className="text-base md:text-lg text-[var(--color-fog)] leading-relaxed max-w-2xl">
              Pour garantir une sécurité totale des données biométriques et une
              fluidité de grade luxe, TRYONYOU déploie l'architecture ABVETOS,
              dirigée par l'Agente 70 (Manus) — architecte suprême supervisant
              50 agents intelligents répartis en sept blocs fonctionnels.
            </p>
          </div>
        </div>

        <div className="hairline mb-14" />

        {/* Tableau éditorial des modules */}
        <div className="glass-card">
          {/* Header */}
          <div className="hidden md:grid grid-cols-12 gap-6 px-8 py-5 border-b border-[rgba(197,164,109,0.18)] text-[10px] tracking-[0.22em] uppercase text-[var(--color-or-luxe)]">
            <div className="col-span-2">Module</div>
            <div className="col-span-3">Domaine</div>
            <div className="col-span-3">Rôle</div>
            <div className="col-span-4">Valeur stratégique</div>
          </div>

          {/* Rows */}
          {MODULES.map((m) => (
            <div
              key={m.code}
              className="grid grid-cols-12 gap-4 md:gap-6 px-6 md:px-8 py-7 border-b border-[rgba(197,164,109,0.12)] last:border-b-0 hover:bg-[rgba(197,164,109,0.04)] transition-colors duration-500"
            >
              <div className="col-span-12 md:col-span-2">
                <div className="font-display italic text-2xl md:text-3xl text-[var(--color-or)]">
                  {m.code}
                </div>
              </div>
              <div className="col-span-12 md:col-span-3 text-[var(--color-ivoire)]/90 text-sm">
                {m.long}
              </div>
              <div className="col-span-12 md:col-span-3 text-[var(--color-fog)] text-sm">
                {m.role}
              </div>
              <div className="col-span-12 md:col-span-4 text-[var(--color-ivoire)]/80 text-sm leading-relaxed">
                {m.value}
              </div>
            </div>
          ))}
        </div>

        {/* Agente 70 + Stack */}
        <div className="grid grid-cols-12 gap-8 mt-16">
          <div className="col-span-12 md:col-span-7">
            <div className="eyebrow mb-4">Orchestration</div>
            <h3 className="display-m mb-4">
              <span className="accent-italic">Agente 70</span> — l'architecte suprême
            </h3>
            <p className="text-[var(--color-ivoire)]/85 leading-relaxed mb-6">
              Une intelligence pivot qui orchestre 50 agents spécialisés.
              Chaque bloc fonctionnel agit comme un atelier d'artisan :
              autonome, expert, mais aligné sur la même partition couture.
            </p>
            <div className="flex flex-wrap gap-2">
              {AGENTS.map((a) => (
                <span key={a} className="chip">{a}</span>
              ))}
            </div>
          </div>

          <div className="col-span-12 md:col-span-5 flex flex-col gap-4">
            <div className="border border-[rgba(197,164,109,0.25)] p-6">
              <div className="text-[11px] tracking-[0.22em] uppercase text-[var(--color-or-luxe)] mb-2">
                Stack technique
              </div>
              <div className="text-[var(--color-ivoire)] text-base">React 18.3.1 · Vite 7.1.2</div>
            </div>
            <div className="border border-[rgba(197,164,109,0.25)] p-6">
              <div className="text-[11px] tracking-[0.22em] uppercase text-[var(--color-or-luxe)] mb-2">
                Temps de chargement
              </div>
              <div className="text-[var(--color-or)] font-display text-3xl md:text-4xl">&lt; 1,5 s</div>
            </div>
            <div className="border border-[rgba(197,164,109,0.25)] p-6">
              <div className="text-[11px] tracking-[0.22em] uppercase text-[var(--color-or-luxe)] mb-2">
                Score Lighthouse
              </div>
              <div className="text-[var(--color-or)] font-display text-3xl md:text-4xl">95+</div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
