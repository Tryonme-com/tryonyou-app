/**
 * CAP — Creative Auto-Production
 * Visual pipeline page: shows the 11-step JIT (Just-In-Time) garment production flow,
 * from biometric scan to manufactured order, in the same Maison Couture Nocturne aesthetic.
 *
 * No backend logic here — this is a visual investor/B2B explainer.
 * The architecture mirrors the real CAP module at /src/modules/CAP/index.js.
 */
import { useEffect, useRef, useState } from "react";
import { Link } from "wouter";
import SiteHeader from "@/components/sections/SiteHeader";
import SiteFooter from "@/components/sections/SiteFooter";
import { useReveal } from "@/hooks/useReveal";

// ─── Pipeline data ──────────────────────────────────────────────────────────
type Step = {
  id: string;
  index: string;
  title: string;
  subtitle: string;
  body: string;
  glyph: string; // small unicode/decoration
};

const PIPELINE: Step[] = [
  {
    id: "scan",
    index: "01",
    title: "Body Scan",
    subtitle: "MediaPipe Pose · 33 points · 22 ms",
    body:
      "Le client active son miroir intelligent ou son téléphone. 33 points biométriques sont verrouillés en 22 millisecondes par le filtre EMA stable. Aucune mesure manuelle, aucune saisie. Aucune donnée n'est stockée.",
    glyph: "◇",
  },
  {
    id: "context",
    index: "02",
    title: "Context Engineering",
    subtitle: "PAU · état émotionnel + occasion",
    body:
      "Le module PAU (Personalized Aesthetic Understanding) recueille l'état émotionnel et l'occasion : travail, soirée, casual. La FTT (Fashion Trend Tracker) injecte les silhouettes et palettes en tendance. Le système comprend le pourquoi avant le quoi.",
    glyph: "◈",
  },
  {
    id: "fit",
    index: "03",
    title: "Fit Score Check",
    subtitle: "Seuil dynamique 0.85",
    body:
      "Si la garde-robe existante propose un vêtement avec un score d'ajustement supérieur à 0.85, CAP s'efface. Sinon, le pipeline de génération sur-mesure s'enclenche. Aucune surproduction, aucun gaspillage.",
    glyph: "◆",
  },
  {
    id: "pattern",
    index: "04",
    title: "Pattern Generation",
    subtitle: "DXF vectoriel · Soutien à la coupe",
    body:
      "Le PatternGenerator produit un patron DXF prêt pour la table de découpe industrielle, généré à partir des données anthropométriques exactes du client et de la silhouette tendance choisie.",
    glyph: "◇",
  },
  {
    id: "seam",
    index: "05",
    title: "Seam Specification",
    subtitle: "Marges · tolérances · ordre de couture",
    body:
      "Le SeamGenerator établit chaque couture avec sa marge précise, sa tolérance de tension et son ordre d'assemblage. Le vêtement est documenté avant d'exister physiquement.",
    glyph: "◈",
  },
  {
    id: "fabric",
    index: "06",
    title: "Fabric Mapping",
    subtitle: "Élasticité · drape · friction",
    body:
      "Le FabricMapper attribue les modules physiques du tissu : coton-blend, soie élastique, laine légère, mix industriel. Robert Engine consommera ces propriétés pour le rendu temps réel.",
    glyph: "◆",
  },
  {
    id: "render",
    index: "07",
    title: "Photorealistic Render",
    subtitle: "Studio lighting · 4K mockup",
    body:
      "Le RenderEngine produit un mockup photoréaliste en éclairage studio. Le client voit son vêtement avant qu'il ne soit coupé. La marque voit son SKU avant qu'il ne soit produit.",
    glyph: "◇",
  },
  {
    id: "metadata",
    index: "08",
    title: "Metadata Build",
    subtitle: "YML · traçabilité · timestamp",
    body:
      "Le MetadataBuilder consolide tout : patron, coutures, tissu, contexte émotionnel, tendances activées, signature horaire. Un dossier de production complet, prêt pour audit ou blockchain.",
    glyph: "◈",
  },
  {
    id: "wardrobe",
    index: "09",
    title: "Smart Wardrobe Sync",
    subtitle: "Archivage versionné",
    body:
      "Le SmartWardrobeConnector archive le vêtement généré dans la garde-robe numérique du client. Versionnage, retouches futures, historique d'ajustement. La donnée appartient au client.",
    glyph: "◆",
  },
  {
    id: "jit",
    index: "10",
    title: "JIT Production Order",
    subtitle: "Just-In-Time · Zero-Stock",
    body:
      "Le JITConnector envoie le dossier complet à l'usine partenaire. Production unitaire à la commande. Pas de stock dormant, pas de soldes liquidatives, pas de retours subis. Le brevet PCT/EP2025/067317 protège cette boucle.",
    glyph: "◇",
  },
  {
    id: "delivery",
    index: "11",
    title: "Delivery & Fit Score 1.0",
    subtitle: "Score d'ajustement parfait",
    body:
      "Le vêtement arrive au client. Score d'ajustement : 1.0. Le client n'a jamais vu un seul chiffre, et pourtant le tombé est exact. C'est la promesse Zero-Size : la technologie connaît la taille sans la dire.",
    glyph: "◈",
  },
];

// ─── Sub-components ─────────────────────────────────────────────────────────
function PipelineNode({ step, idx, total }: { step: Step; idx: number; total: number }) {
  const isLast = idx === total - 1;
  const align = idx % 2 === 0 ? "md:flex-row" : "md:flex-row-reverse";
  return (
    <li className="reveal-up relative" data-delay={(idx % 4) * 90}>
      <div className={`flex flex-col ${align} items-stretch gap-6 md:gap-12`}>
        {/* Card */}
        <div className="flex-1 group">
          <div className="relative h-full p-6 md:p-8 rounded-sm border border-[rgba(201,168,76,0.22)] bg-gradient-to-br from-[rgba(20,16,15,0.7)] to-[rgba(10,8,7,0.85)] backdrop-blur-sm transition-all duration-700 group-hover:border-[rgba(201,168,76,0.55)] group-hover:translate-y-[-2px]">
            {/* index */}
            <div className="absolute top-5 right-5 text-[var(--color-or)] font-display italic text-[42px] leading-none opacity-30 group-hover:opacity-60 transition-opacity duration-500">
              {step.index}
            </div>
            <div className="text-[var(--color-or)] text-[14px] tracking-[0.32em] mb-3 opacity-70">
              {step.glyph}
            </div>
            <h3
              className="font-display italic text-[var(--color-ivoire)] text-[26px] md:text-[28px] leading-tight mb-2"
              style={{ fontFamily: "var(--font-display)" }}
            >
              {step.title}
            </h3>
            <div className="eyebrow text-[var(--color-or)]/80 mb-4">
              {step.subtitle}
            </div>
            <p className="text-[14px] leading-[1.7] text-[var(--color-ivoire)]/72">
              {step.body}
            </p>
          </div>
        </div>

        {/* Diamond connector with vertical line */}
        <div className="hidden md:flex flex-col items-center justify-center w-[80px] shrink-0 relative">
          <div
            className="w-3 h-3 rotate-45 bg-[var(--color-or)] shadow-[0_0_24px_rgba(201,164,109,0.6)]"
            aria-hidden
          />
          {!isLast && (
            <div
              className="absolute top-[calc(50%+12px)] w-px h-[calc(100%-12px+96px)] bg-gradient-to-b from-[rgba(201,164,109,0.55)] via-[rgba(201,164,109,0.25)] to-[rgba(201,164,109,0)]"
              aria-hidden
            />
          )}
        </div>

        {/* Spacer for alternating layout */}
        <div className="flex-1 hidden md:block" />
      </div>
    </li>
  );
}

// ─── Animated horizontal pipeline strip (top hero visual) ──────────────────
function HeroPipelineStrip() {
  const ref = useRef<HTMLCanvasElement | null>(null);
  const rafRef = useRef<number | null>(null);
  const [, setTick] = useState(0);

  useEffect(() => {
    const canvas = ref.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    const dpr = Math.min(window.devicePixelRatio || 1, 2);
    let W = 0, H = 0;
    const resize = () => {
      const r = canvas.getBoundingClientRect();
      W = canvas.width = Math.floor(r.width * dpr);
      H = canvas.height = Math.floor(r.height * dpr);
    };
    resize();
    const ro = new ResizeObserver(resize);
    ro.observe(canvas);

    const NODES = 11;
    const start = performance.now();

    const render = () => {
      const t = (performance.now() - start) / 1000;
      ctx.clearRect(0, 0, W, H);

      const pad = W * 0.06;
      const innerW = W - pad * 2;
      const cy = H / 2;
      const r = Math.min(W, H) * 0.022;

      // Base line
      const baseGrad = ctx.createLinearGradient(pad, cy, W - pad, cy);
      baseGrad.addColorStop(0, "rgba(197,164,109,0.0)");
      baseGrad.addColorStop(0.5, "rgba(197,164,109,0.45)");
      baseGrad.addColorStop(1, "rgba(197,164,109,0.0)");
      ctx.strokeStyle = baseGrad;
      ctx.lineWidth = 1 * dpr;
      ctx.beginPath();
      ctx.moveTo(pad, cy);
      ctx.lineTo(W - pad, cy);
      ctx.stroke();

      // Pulse traveling along
      const pulseX = pad + ((t * 0.18) % 1) * innerW;
      const grad = ctx.createRadialGradient(pulseX, cy, 0, pulseX, cy, 90 * dpr);
      grad.addColorStop(0, "rgba(232,210,155,0.85)");
      grad.addColorStop(0.4, "rgba(197,164,109,0.45)");
      grad.addColorStop(1, "rgba(197,164,109,0)");
      ctx.fillStyle = grad;
      ctx.fillRect(pulseX - 90 * dpr, cy - 60 * dpr, 180 * dpr, 120 * dpr);

      // Nodes
      for (let i = 0; i < NODES; i++) {
        const x = pad + (innerW * i) / (NODES - 1);
        const dist = Math.abs(x - pulseX) / (innerW / NODES);
        const glow = Math.max(0, 1 - dist);
        const rr = r * (1 + glow * 0.6);

        ctx.save();
        ctx.translate(x, cy);
        ctx.rotate(Math.PI / 4);
        ctx.fillStyle = `rgba(197,164,109,${0.55 + glow * 0.45})`;
        ctx.shadowColor = "rgba(197,164,109,0.8)";
        ctx.shadowBlur = (4 + glow * 18) * dpr;
        ctx.fillRect(-rr, -rr, rr * 2, rr * 2);
        ctx.restore();
      }

      rafRef.current = requestAnimationFrame(render);
    };
    rafRef.current = requestAnimationFrame(render);
    setTick(1);

    return () => {
      ro.disconnect();
      if (rafRef.current) cancelAnimationFrame(rafRef.current);
    };
  }, []);

  return (
    <div className="relative w-full h-[120px] md:h-[160px] mt-12">
      <canvas ref={ref} className="absolute inset-0 w-full h-full" />
    </div>
  );
}

// ─── Architecture summary block ────────────────────────────────────────────
function ArchitectureBlock() {
  const modules = [
    { name: "PatternGenerator", role: "Patrons DXF vectoriels" },
    { name: "SeamGenerator", role: "Spécifications de couture" },
    { name: "FabricMapper", role: "Modules physiques tissu" },
    { name: "RenderEngine", role: "Mockup photoréaliste 4K" },
    { name: "MetadataBuilder", role: "Dossier YML traçable" },
    { name: "PAUConnector", role: "État émotionnel client" },
    { name: "FTTConnector", role: "Tendances temps réel" },
    { name: "SmartWardrobe", role: "Archivage versionné" },
    { name: "JITConnector", role: "Production à la commande" },
    { name: "CAPServer", role: "API REST orchestratrice" },
  ];
  return (
    <section className="relative py-32 md:py-40 border-t border-[rgba(201,168,76,0.15)]">
      <div className="container">
        <div className="reveal-up mb-16">
          <div className="eyebrow mb-4">Architecture · 10 modules orchestrés</div>
          <h2
            className="font-display italic text-[var(--color-ivoire)] text-[42px] md:text-[60px] leading-[1.05] max-w-3xl"
            style={{ fontFamily: "var(--font-display)" }}
          >
            Un orchestrateur, dix instruments, zéro stock.
          </h2>
          <p className="mt-6 text-[15px] leading-[1.8] text-[var(--color-ivoire)]/70 max-w-2xl">
            CAP est un module orchestrateur en ES Modules (Node 18+) qui pilote dix
            instruments spécialisés. Chaque instrument est testable, remplaçable, et
            connecté via un bus REST interne. Le pipeline est <em>fully operational</em>{" "}
            depuis la version 1.0.0.
          </p>
        </div>
        <ul className="reveal-up grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3" data-delay={120}>
          {modules.map((m) => (
            <li
              key={m.name}
              className="group flex items-baseline gap-4 px-5 py-4 border border-[rgba(201,168,76,0.18)] bg-[rgba(20,16,15,0.4)] hover:bg-[rgba(20,16,15,0.7)] hover:border-[rgba(201,168,76,0.5)] transition-colors duration-500"
            >
              <span className="text-[var(--color-or)] font-display italic text-[22px] leading-none">
                ◆
              </span>
              <div className="flex-1">
                <div className="font-display italic text-[var(--color-ivoire)] text-[18px] leading-tight">
                  {m.name}
                </div>
                <div className="text-[11px] tracking-[0.18em] uppercase text-[var(--color-ivoire)]/55 mt-1">
                  {m.role}
                </div>
              </div>
            </li>
          ))}
        </ul>
      </div>
    </section>
  );
}

// ─── KPIs band ─────────────────────────────────────────────────────────────
function KPIBand() {
  const kpis = [
    { value: "≤ 5 s", label: "Génération vêtement complet" },
    { value: "0", label: "Unité produite avant commande" },
    { value: "1.0", label: "Score d'ajustement post-CAP" },
    { value: "11", label: "Étapes orchestrées" },
  ];
  return (
    <section className="relative py-24 md:py-32 border-t border-[rgba(201,168,76,0.15)]">
      <div className="container">
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-8 md:gap-12">
          {kpis.map((k, i) => (
            <div key={i} className="reveal-up" data-delay={i * 80}>
              <div
                className="font-display italic text-[var(--color-or)] text-[52px] md:text-[68px] leading-none"
                style={{ fontFamily: "var(--font-display)" }}
              >
                {k.value}
              </div>
              <div className="mt-3 eyebrow text-[var(--color-ivoire)]/70 max-w-[180px]">
                {k.label}
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

// ─── Page ──────────────────────────────────────────────────────────────────
export default function CAP() {
  useReveal();

  useEffect(() => {
    document.title = "CAP — Creative Auto-Production · TRYONYOU";
  }, []);

  return (
    <div className="bg-[var(--color-noir)] text-[var(--color-ivoire)] min-h-screen">
      <SiteHeader />

      {/* HERO */}
      <section className="relative pt-40 md:pt-48 pb-20 md:pb-28">
        <div className="container">
          <div className="reveal-up max-w-4xl">
            <div className="eyebrow mb-6">CAP — Creative Auto-Production</div>
            <h1
              className="font-display italic text-[var(--color-ivoire)] text-[58px] md:text-[96px] leading-[0.95] tracking-tight"
              style={{ fontFamily: "var(--font-display)" }}
            >
              De la mesure
              <br />
              <span className="text-[var(--color-or)]">au vêtement</span>,
              <br />
              en onze gestes.
            </h1>
            <p className="mt-8 text-[16px] md:text-[18px] leading-[1.8] text-[var(--color-ivoire)]/72 max-w-2xl">
              CAP transforme une silhouette biométrique en commande de production
              unitaire. Aucune unité n'est coupée avant que le client n'ait confirmé.
              Aucun stock n'est créé pour combler un manque. Le vêtement existe parce
              qu'il a déjà trouvé son corps.
            </p>
            <div className="mt-10 flex flex-wrap items-center gap-4">
              <Link href="/tryon" className="btn-or text-[12px] tracking-[0.22em]">
                Voir la démo Try-On →
              </Link>
              <a
                href="#pipeline"
                className="text-[12px] tracking-[0.32em] uppercase text-[var(--color-or)]/80 hover:text-[var(--color-or)] transition-colors duration-500"
              >
                Explorer le pipeline ↓
              </a>
            </div>
          </div>

          <HeroPipelineStrip />
        </div>
      </section>

      {/* KPI BAND */}
      <KPIBand />

      {/* PIPELINE */}
      <section id="pipeline" className="relative py-24 md:py-32 border-t border-[rgba(201,168,76,0.15)]">
        <div className="container">
          <div className="reveal-up mb-20 max-w-3xl">
            <div className="eyebrow mb-4">Pipeline · 11 étapes orchestrées</div>
            <h2
              className="font-display italic text-[var(--color-ivoire)] text-[44px] md:text-[64px] leading-[1.05]"
              style={{ fontFamily: "var(--font-display)" }}
            >
              Le pipeline complet, de la peau à la couture.
            </h2>
            <p className="mt-6 text-[15px] leading-[1.8] text-[var(--color-ivoire)]/70">
              Chaque étape est un module isolé, observable, et capable de fallback
              gracieux si un service externe est indisponible. Robustesse industrielle,
              esthétique de Maison.
            </p>
          </div>
          <ol className="space-y-6 md:space-y-12">
            {PIPELINE.map((step, i) => (
              <PipelineNode key={step.id} step={step} idx={i} total={PIPELINE.length} />
            ))}
          </ol>
        </div>
      </section>

      {/* ARCHITECTURE */}
      <ArchitectureBlock />

      {/* CTA */}
      <section className="relative py-32 md:py-40 border-t border-[rgba(201,168,76,0.15)]">
        <div className="container">
          <div className="reveal-up max-w-3xl">
            <div className="eyebrow mb-4">Pilote Lafayette 2026</div>
            <h2
              className="font-display italic text-[var(--color-ivoire)] text-[42px] md:text-[60px] leading-[1.05]"
              style={{ fontFamily: "var(--font-display)" }}
            >
              CAP n'est pas une promesse —{" "}
              <span className="text-[var(--color-or)]">c'est un module opérationnel.</span>
            </h2>
            <p className="mt-6 text-[15px] leading-[1.8] text-[var(--color-ivoire)]/72">
              Brevet socle PCT/EP2025/067317 · 22 revendications protégées · 8 marques
              déposées. CAP est intégré à TRYONYOU-ABVETOS-ULTRA-PLUS-ULTIMATUM depuis la
              version 1.0.0.
            </p>
            <div className="mt-10 flex flex-wrap items-center gap-4">
              <Link href="/offre" className="btn-or text-[12px] tracking-[0.22em]">
                Réserver le pilote Divine 2027 →
              </Link>
              <Link
                href="/manifeste"
                className="text-[12px] tracking-[0.32em] uppercase text-[var(--color-ivoire)]/65 hover:text-[var(--color-or)] transition-colors duration-500"
              >
                Lire le Manifeste →
              </Link>
            </div>
          </div>
        </div>
      </section>

      <SiteFooter />
    </div>
  );
}
