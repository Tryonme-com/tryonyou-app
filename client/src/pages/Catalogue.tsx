/**
 * TRYONYOU — /catalogue
 *
 * Editorial grid of 60 curated garments × 6 designers, with filters.
 * Tile click → /tryon?sku=…
 */

import { useMemo, useState } from "react";
import { Link } from "wouter";
import {
  GARMENTS,
  DESIGNERS,
  TYPES,
  STATS,
  type Garment,
} from "@/lib/catalog";
import { catalogVignetteUrl } from "@/lib/garmentOverlays";
import SiteHeader from "@/components/sections/SiteHeader";
import SiteFooter from "@/components/sections/SiteFooter";

const TYPE_LABEL: Record<string, string> = {
  robe: "Robes",
  ensemble: "Ensembles",
  chemise: "Chemises",
  pantalon: "Pantalons",
  jupe: "Jupes",
  manteau: "Manteaux",
  foulard: "Foulards",
  accessoire: "Accessoires",
};

const PRICE_BANDS = [
  { id: "all", label: "Tous" },
  { id: "low", label: "< 800 €" },
  { id: "mid", label: "800 — 1 500 €" },
  { id: "high", label: "≥ 1 500 €" },
];

function FilterPill({
  active,
  onClick,
  children,
}: {
  active: boolean;
  onClick: () => void;
  children: React.ReactNode;
}) {
  return (
    <button
      onClick={onClick}
      className={`px-4 py-2 text-[11px] tracking-[0.18em] uppercase transition-colors duration-300 border ${
        active
          ? "border-[var(--color-or)] bg-[var(--color-or)]/10 text-[var(--color-or)]"
          : "border-white/10 text-white/55 hover:border-white/30 hover:text-white/85"
      }`}
    >
      {children}
    </button>
  );
}

function GarmentTile({ g }: { g: Garment }) {
  const vignette = catalogVignetteUrl(g);
  return (
    <Link
      href={`/tryon?sku=${g.sku}`}
      className="group block bg-[var(--color-graphite)] border border-white/5 hover:border-[var(--color-or)]/40 transition-colors duration-500"
    >
      <div className="aspect-[3/4] bg-[var(--color-noir)] flex items-center justify-center overflow-hidden relative">
        <img
          src={vignette}
          alt={g.name}
          className="w-3/4 h-3/4 object-contain transition-transform duration-700 group-hover:scale-[1.04]"
          loading="lazy"
        />
        {g.isHero && (
          <span className="absolute top-3 left-3 chip">Pièce signature</span>
        )}
      </div>
      <div className="p-5">
        <div className="text-[10px] tracking-[0.28em] uppercase text-[var(--color-or)]/70 mb-1">
          {g.designer}
        </div>
        <h3 className="font-display text-[18px] text-[var(--color-ivoire)] mb-2 leading-tight">
          {g.name}
        </h3>
        <div className="flex items-baseline justify-between text-[12px] text-white/50">
          <span className="truncate pr-2">{g.fabricName}</span>
          <span className="font-display text-[15px] text-[var(--color-or)]">
            € {g.price}
          </span>
        </div>
      </div>
    </Link>
  );
}

export default function Catalogue() {
  const [designer, setDesigner] = useState("all");
  const [type, setType] = useState("all");
  const [priceBand, setPriceBand] = useState("all");

  const filtered = useMemo(() => {
    return GARMENTS.filter((g) => {
      if (designer !== "all" && g.designer !== designer) return false;
      if (type !== "all" && g.type !== type) return false;
      if (priceBand === "low" && g.price >= 800) return false;
      if (priceBand === "mid" && (g.price < 800 || g.price >= 1500)) return false;
      if (priceBand === "high" && g.price < 1500) return false;
      return true;
    });
  }, [designer, type, priceBand]);

  return (
    <div className="min-h-screen flex flex-col bg-[var(--color-noir)]">
      <SiteHeader />

      <main className="flex-1 pt-32">
        {/* Heading */}
        <section className="container pb-12">
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-10">
            <div className="lg:col-span-7">
              <span className="eyebrow mb-5 inline-flex">Catalogue Lafayette</span>
              <h1 className="display-l mb-6">
                Soixante pièces,
                <br />
                <span className="accent-italic">six maisons.</span>
              </h1>
              <p className="text-[17px] leading-[1.75] text-[var(--color-ivoire)]/80 max-w-2xl">
                Le moteur PAU V11 a sélectionné soixante pièces signatures issues
                de six maisons partenaires : Elena Grandini, Maison Classique,
                Atelier Nuit, Urban Atelier, Maison Dorée, LVT Vogue. Chaque
                silhouette est associée à un tissu technique et à un profil de
                drapé prêt pour la projection biométrique.
              </p>
            </div>

            <div className="lg:col-span-4 lg:col-start-9 lg:pt-3">
              <div className="grid grid-cols-3 gap-4">
                <Stat value={String(STATS.totalGarments)} label="Pièces" />
                <Stat value={String(STATS.designers.length)} label="Maisons" />
                <Stat value={String(STATS.totalFabrics)} label="Tissus" />
              </div>
            </div>
          </div>
        </section>

        {/* Filters */}
        <section className="container pb-10">
          <div className="hairline mb-8" />

          <FilterRow label="Designer">
            <FilterPill active={designer === "all"} onClick={() => setDesigner("all")}>
              Tous
            </FilterPill>
            {DESIGNERS.map((d) => (
              <FilterPill key={d} active={designer === d} onClick={() => setDesigner(d)}>
                {d}
              </FilterPill>
            ))}
          </FilterRow>

          <FilterRow label="Catégorie">
            <FilterPill active={type === "all"} onClick={() => setType("all")}>
              Toutes
            </FilterPill>
            {TYPES.map((tp) => (
              <FilterPill key={tp} active={type === tp} onClick={() => setType(tp)}>
                {TYPE_LABEL[tp] ?? tp}
              </FilterPill>
            ))}
          </FilterRow>

          <FilterRow label="Tarif">
            {PRICE_BANDS.map((b) => (
              <FilterPill
                key={b.id}
                active={priceBand === b.id}
                onClick={() => setPriceBand(b.id)}
              >
                {b.label}
              </FilterPill>
            ))}
          </FilterRow>
        </section>

        {/* Grid */}
        <section className="container pb-24">
          <div className="text-[10px] tracking-[0.28em] uppercase text-white/40 mb-6">
            {filtered.length} pièce{filtered.length > 1 ? "s" : ""}
          </div>
          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-4 lg:gap-6">
            {filtered.map((g) => (
              <GarmentTile key={g.id} g={g} />
            ))}
          </div>

          {filtered.length === 0 && (
            <div className="text-center py-24 text-white/40 italic">
              Aucune pièce ne correspond à votre recherche.
            </div>
          )}
        </section>
      </main>

      <SiteFooter />
    </div>
  );
}

function Stat({ value, label }: { value: string; label: string }) {
  return (
    <div className="border-t border-[var(--color-or)]/30 pt-3">
      <div className="font-display text-[var(--color-or)] text-[28px] leading-none">{value}</div>
      <div className="text-[10px] tracking-[0.2em] uppercase text-white/40 mt-2">{label}</div>
    </div>
  );
}

function FilterRow({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div className="mb-6 flex flex-wrap items-center gap-x-6 gap-y-3">
      <div className="text-[10px] tracking-[0.28em] uppercase text-[var(--color-or)]/70 min-w-[80px]">
        {label}
      </div>
      <div className="flex flex-wrap gap-2">{children}</div>
    </div>
  );
}
