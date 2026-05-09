/**
 * TRYONYOU — /offre
 *
 * Offre Pionnière Divine 2027.
 *
 * Style: Maison Couture Nocturne — graphite #0A0807 + or #C9A84C.
 * Editorial typography: Playfair Display italic display + Inter body.
 * Layout: asymmetric editorial — no centred grid, hairline gold rules, Roman numerals.
 */

import { Link } from "wouter";
import { useEffect } from "react";
import SiteHeader from "@/components/sections/SiteHeader";
import SiteFooter from "@/components/sections/SiteFooter";

const PATENT = "PCT/EP2025/067317";
const SIREN = "943 610 196";
const EMAIL = "admin@tryonyou.app";

function GoldRule({ className = "" }: { className?: string }) {
  return <div className={`h-px bg-[var(--color-or)]/40 ${className}`} />;
}

function HairlineFrame({ children }: { children: React.ReactNode }) {
  return (
    <div className="relative">
      <div className="absolute inset-0 border border-[var(--color-or)]/25 pointer-events-none" />
      <div className="absolute -top-1 -left-1 w-3 h-3 border-t border-l border-[var(--color-or)] pointer-events-none" />
      <div className="absolute -top-1 -right-1 w-3 h-3 border-t border-r border-[var(--color-or)] pointer-events-none" />
      <div className="absolute -bottom-1 -left-1 w-3 h-3 border-b border-l border-[var(--color-or)] pointer-events-none" />
      <div className="absolute -bottom-1 -right-1 w-3 h-3 border-b border-r border-[var(--color-or)] pointer-events-none" />
      {children}
    </div>
  );
}

export default function Offre() {
  useEffect(() => {
    document.title = "Offre Pionnière — Divine 2027 · TRYONYOU";
  }, []);

  return (
    <div className="min-h-screen bg-[var(--color-noir)] text-white">
      <SiteHeader />

      {/* ==================== HERO ==================== */}
      <section className="relative pt-32 pb-24 overflow-hidden">
        {/* Ambient background — radial gold gloss */}
        <div
          aria-hidden
          className="absolute inset-0 pointer-events-none"
          style={{
            background:
              "radial-gradient(ellipse 70% 50% at 75% 30%, rgba(201,168,76,0.10), transparent 60%), radial-gradient(ellipse 50% 40% at 15% 80%, rgba(201,168,76,0.06), transparent 60%)",
          }}
        />
        {/* Subtle film grain */}
        <div
          aria-hidden
          className="absolute inset-0 pointer-events-none opacity-[0.06] mix-blend-overlay"
          style={{
            backgroundImage:
              "url(\"data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='200' height='200'><filter id='n'><feTurbulence type='fractalNoise' baseFrequency='0.85' numOctaves='2' stitchTiles='stitch'/></filter><rect width='100%' height='100%' filter='url(%23n)'/></svg>\")",
          }}
        />

        <div className="container max-w-[1240px] relative z-10">
          <div className="grid grid-cols-12 gap-x-8 gap-y-10">
            {/* Left rail — overline + roman numeral */}
            <div className="col-span-12 lg:col-span-3 flex lg:flex-col gap-6 items-baseline lg:items-start">
              <div className="text-[10px] tracking-[0.4em] uppercase text-[var(--color-or)]">
                Offre Pionnière
              </div>
              <div className="font-display text-[var(--color-or)]/40 italic text-[64px] lg:text-[110px] leading-none">
                I.
              </div>
              <div className="hidden lg:block text-[10px] tracking-[0.32em] uppercase text-white/40 max-w-[220px] leading-relaxed">
                Pour les maisons fondatrices du mouvement Divine 2027.
              </div>
            </div>

            {/* Main display */}
            <div className="col-span-12 lg:col-span-9">
              <h1 className="font-display text-white leading-[0.95] text-[44px] sm:text-[68px] lg:text-[96px] tracking-tight">
                <span className="block">La fin du retour.</span>
                <span className="block italic text-[var(--color-or)]">
                  Le commencement
                </span>
                <span className="block">d'une autre mode.</span>
              </h1>

              <div className="mt-12 max-w-[640px]">
                <GoldRule className="mb-6 w-16" />
                <p className="text-[16px] sm:text-[18px] leading-[1.7] text-white/75">
                  TRYONYOU rejoint un cercle restreint de maisons pionnières
                  prêtes à signer la fin du retour produit. Voici les conditions
                  réservées aux trente premières marques qui s'engagent dans le
                  mouvement <em className="text-[var(--color-or)]">Divine 2027</em>.
                </p>

                <div className="mt-8 flex flex-wrap items-center gap-4">
                  <a href="#conditions" className="btn-or inline-flex">
                    Lire les conditions <span aria-hidden>↓</span>
                  </a>
                  <a
                    href={`mailto:${EMAIL}?subject=Offre%20Pionni%C3%A8re%20Divine%202027`}
                    className="text-[12px] tracking-[0.3em] uppercase text-white/60 hover:text-[var(--color-or)] transition-colors border-b border-white/30 hover:border-[var(--color-or)] pb-1"
                  >
                    Programmer une démonstration
                  </a>
                </div>
              </div>
            </div>
          </div>

          {/* Hero baseline — dignified meta strip */}
          <div className="mt-20 flex flex-wrap items-center gap-x-10 gap-y-3 text-[10px] tracking-[0.32em] uppercase text-white/40">
            <span>Brevet {PATENT}</span>
            <span className="hidden sm:inline">·</span>
            <span>SIREN {SIREN}</span>
            <span className="hidden sm:inline">·</span>
            <span>22 revendications</span>
            <span className="hidden sm:inline">·</span>
            <span className="text-[var(--color-or)]">Mai 2026</span>
          </div>
        </div>
      </section>

      <GoldRule className="opacity-30" />

      {/* ==================== MOVEMENT ==================== */}
      <section className="py-24">
        <div className="container max-w-[1240px]">
          <div className="grid grid-cols-12 gap-x-8 gap-y-10">
            <div className="col-span-12 lg:col-span-5">
              <div className="text-[10px] tracking-[0.4em] uppercase text-[var(--color-or)] mb-6">
                Manifeste
              </div>
              <h2 className="font-display italic text-[42px] lg:text-[58px] leading-[1.05] text-white">
                Divine <span className="text-[var(--color-or)]">2027</span>
              </h2>
              <GoldRule className="mt-8 w-12" />
            </div>

            <div className="col-span-12 lg:col-span-7 space-y-7 text-white/75 text-[16px] leading-[1.85]">
              <p>
                Le retour produit est un héritage logistique du XX<sup>e</sup>{" "}
                siècle. Il coûte aux maisons un point de marge par collection,
                impose des emballages que personne ne souhaite, et place le
                client en juge plutôt qu'en complice.
              </p>
              <p>
                <em className="text-[var(--color-or)] not-italic font-display">
                  Divine 2027
                </em>{" "}
                est l'engagement collectif d'en finir avec ce modèle d'ici la
                fin de la décennie. TRYONYOU en fournit l'instrument :
                visualisation biométrique exacte avant achat, tombé de tissu
                photoréaliste, fidélité des proportions au millimètre.
              </p>
              <p>
                Les premières maisons qui rejoignent <em>Divine 2027</em>{" "}
                obtiennent — au-delà des conditions tarifaires — la mention de
                membre fondateur dans toutes nos communications presse,
                investisseurs, et institutionnelles.
              </p>
            </div>
          </div>
        </div>
      </section>

      <GoldRule className="opacity-30" />

      {/* ==================== CONDITIONS ==================== */}
      <section id="conditions" className="py-24 lg:py-32 relative">
        <div
          aria-hidden
          className="absolute inset-0 pointer-events-none"
          style={{
            background:
              "linear-gradient(180deg, rgba(201,168,76,0.04) 0%, transparent 50%)",
          }}
        />
        <div className="container max-w-[1240px] relative z-10">
          <div className="grid grid-cols-12 gap-x-8 mb-16">
            <div className="col-span-12 lg:col-span-3">
              <div className="font-display text-[var(--color-or)]/40 italic text-[64px] lg:text-[110px] leading-none">
                II.
              </div>
            </div>
            <div className="col-span-12 lg:col-span-9">
              <div className="text-[10px] tracking-[0.4em] uppercase text-[var(--color-or)] mb-4">
                Conditions Pionnières
              </div>
              <h2 className="font-display text-[36px] lg:text-[52px] leading-[1.05] text-white">
                Deux temps. Une trajectoire.
                <br />
                <span className="italic text-[var(--color-or)]">Aucune barrière.</span>
              </h2>
            </div>
          </div>

          {/* Conditions diptych */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 lg:gap-10">
            {/* CARD 1 — Premier mois */}
            <HairlineFrame>
              <div className="p-8 lg:p-12 bg-gradient-to-br from-[var(--color-or)]/8 via-transparent to-transparent">
                <div className="flex items-baseline justify-between mb-6">
                  <span className="text-[10px] tracking-[0.4em] uppercase text-[var(--color-or)]">
                    Phase Amorçage
                  </span>
                  <span className="font-display italic text-[var(--color-or)]/50 text-[28px]">
                    M1
                  </span>
                </div>
                <h3 className="font-display text-white text-[48px] lg:text-[64px] leading-none mb-2">
                  <span className="text-[var(--color-or)]">Premier mois</span>
                </h3>
                <h3 className="font-display italic text-white text-[40px] lg:text-[54px] leading-none mb-8">
                  offert.
                </h3>
                <GoldRule className="mb-8 w-12" />
                <ul className="space-y-5 text-white/80 text-[15px] leading-[1.7]">
                  <li className="flex gap-4">
                    <span className="text-[var(--color-or)] font-display text-xl leading-none">
                      ·
                    </span>
                    <span>
                      <strong className="text-white">7 % de commission</strong>{" "}
                      uniquement sur les ventes générées par le miroir TRYONYOU.
                      Aucune redevance fixe.
                    </span>
                  </li>
                  <li className="flex gap-4">
                    <span className="text-[var(--color-or)] font-display text-xl leading-none">
                      ·
                    </span>
                    <span>
                      Installation, calibration biométrique, formation des
                      équipes en boutique : <strong className="text-white">incluses</strong>.
                    </span>
                  </li>
                  <li className="flex gap-4">
                    <span className="text-[var(--color-or)] font-display text-xl leading-none">
                      ·
                    </span>
                    <span>
                      Paiement à 15 jours. Aucun engagement de durée. Sortie à
                      tout moment sur simple notification.
                    </span>
                  </li>
                  <li className="flex gap-4">
                    <span className="text-[var(--color-or)] font-display text-xl leading-none">
                      ·
                    </span>
                    <span>
                      Reporting hebdomadaire : taux de conversion, taux de
                      retour évité, valeur générée.
                    </span>
                  </li>
                </ul>
              </div>
            </HairlineFrame>

            {/* CARD 2 — Après M1 */}
            <HairlineFrame>
              <div className="p-8 lg:p-12 relative">
                <div className="flex items-baseline justify-between mb-6">
                  <span className="text-[10px] tracking-[0.4em] uppercase text-white/50">
                    Phase Établissement
                  </span>
                  <span className="font-display italic text-white/30 text-[28px]">
                    M2+
                  </span>
                </div>
                <h3 className="font-display text-white text-[48px] lg:text-[64px] leading-none mb-2">
                  Licence
                </h3>
                <h3 className="font-display italic text-white text-[40px] lg:text-[54px] leading-none mb-2">
                  standard
                </h3>
                <div className="inline-flex items-center gap-3 px-3 py-1.5 mb-8 border border-[var(--color-or)] rounded-sm">
                  <span className="text-[10px] tracking-[0.32em] uppercase text-[var(--color-or)] font-bold">
                    − 20 %
                  </span>
                  <span className="text-[10px] tracking-[0.2em] uppercase text-[var(--color-or)]/80">
                    pionniers Divine 2027
                  </span>
                </div>
                <GoldRule className="mb-8 w-12" />
                <ul className="space-y-5 text-white/80 text-[15px] leading-[1.7]">
                  <li className="flex gap-4">
                    <span className="text-[var(--color-or)] font-display text-xl leading-none">
                      ·
                    </span>
                    <span>
                      <strong className="text-white">Remise pionnière de 20 %</strong>{" "}
                      sur la licence standard, garantie pour la durée du
                      partenariat.
                    </span>
                  </li>
                  <li className="flex gap-4">
                    <span className="text-[var(--color-or)] font-display text-xl leading-none">
                      ·
                    </span>
                    <span>
                      Mention <em>« Maison Fondatrice Divine 2027 »</em> dans
                      nos communications presse, investisseurs et
                      institutionnelles.
                    </span>
                  </li>
                  <li className="flex gap-4">
                    <span className="text-[var(--color-or)] font-display text-xl leading-none">
                      ·
                    </span>
                    <span>
                      Accès prioritaire aux modules en développement : Foot
                      Scan, jumeau numérique de la cabine, intégrations CRM.
                    </span>
                  </li>
                  <li className="flex gap-4">
                    <span className="text-[var(--color-or)] font-display text-xl leading-none">
                      ·
                    </span>
                    <span>
                      Roadmap co-construite : un comité produit trimestriel avec
                      les maisons fondatrices.
                    </span>
                  </li>
                </ul>
              </div>
            </HairlineFrame>
          </div>

          {/* Footnote */}
          <p className="mt-10 text-[11px] tracking-[0.2em] uppercase text-white/40 max-w-[720px] leading-relaxed">
            Offre réservée aux trente premières maisons signataires. Cumulable
            avec les dispositifs d'aide à l'innovation Bpifrance et French Tech.
          </p>
        </div>
      </section>

      <GoldRule className="opacity-30" />

      {/* ==================== INCLUS ==================== */}
      <section className="py-24">
        <div className="container max-w-[1240px]">
          <div className="grid grid-cols-12 gap-x-8 mb-16">
            <div className="col-span-12 lg:col-span-3">
              <div className="font-display text-[var(--color-or)]/40 italic text-[64px] lg:text-[110px] leading-none">
                III.
              </div>
            </div>
            <div className="col-span-12 lg:col-span-9">
              <div className="text-[10px] tracking-[0.4em] uppercase text-[var(--color-or)] mb-4">
                Ce que vous installez
              </div>
              <h2 className="font-display text-[36px] lg:text-[52px] leading-[1.05] text-white">
                Une technologie protégée,
                <br />
                <span className="italic text-[var(--color-or)]">
                  prête à signer.
                </span>
              </h2>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[
              {
                title: "Miroir intelligent",
                body: "Détection corporelle temps réel via MediaPipe Pose, maillage filaire doré et superposition vêtement photoréaliste. 60 FPS sur mobile.",
              },
              {
                title: "Jumeau numérique",
                body: "Représentation biométrique non identifiante du client. Aucune mesure n'est affichée. Conformité RGPD by design.",
              },
              {
                title: "Tombé de tissu",
                body: "Simulation drapé propriétaire pour 55 tissus catalogués (poids, coefficient de drapé, transparence).",
              },
              {
                title: "Catalogue intégré",
                body: "60 vêtements et 15 paires de chaussures déjà chargés. Connecteurs Shopify, OpenCart et Salesforce Commerce sur demande.",
              },
              {
                title: "Reporting hebdomadaire",
                body: "Tableaux de bord par boutique : conversion, retours évités, panier moyen incrémental, valeur générée par session.",
              },
              {
                title: "Brevet PCT/EP",
                body: "Technologie protégée par 22 revendications. Vous installez une exclusivité juridiquement opposable, pas une simple démonstration.",
              },
            ].map((item, i) => (
              <div
                key={i}
                className="group relative p-7 border border-white/10 hover:border-[var(--color-or)]/50 transition-colors duration-500 bg-white/[0.015]"
              >
                <div className="font-display italic text-[var(--color-or)]/40 text-[28px] mb-3">
                  {String(i + 1).padStart(2, "0")}
                </div>
                <h3 className="font-display text-white text-[22px] mb-3 leading-tight">
                  {item.title}
                </h3>
                <p className="text-white/65 text-[14px] leading-[1.7]">
                  {item.body}
                </p>
                <div className="absolute bottom-0 left-0 h-px w-0 group-hover:w-full bg-[var(--color-or)] transition-all duration-700" />
              </div>
            ))}
          </div>
        </div>
      </section>

      <GoldRule className="opacity-30" />

      {/* ==================== FAQ-ish (sober) ==================== */}
      <section className="py-24">
        <div className="container max-w-[1240px]">
          <div className="grid grid-cols-12 gap-x-8 gap-y-10">
            <div className="col-span-12 lg:col-span-4">
              <div className="font-display text-[var(--color-or)]/40 italic text-[64px] lg:text-[110px] leading-none">
                IV.
              </div>
              <div className="text-[10px] tracking-[0.4em] uppercase text-[var(--color-or)] mt-6">
                Questions clés
              </div>
            </div>
            <div className="col-span-12 lg:col-span-8 space-y-10">
              {[
                {
                  q: "À qui s'adresse l'offre pionnière ?",
                  a: "Aux maisons de mode et grands magasins prêts à intégrer le miroir TRYONYOU dans au moins un point de vente parisien d'ici fin 2026. Une seconde vague est prévue pour Milan, Londres et New York en 2027.",
                },
                {
                  q: "Que recouvre la commission de 7 % ?",
                  a: "Strictement les ventes attribuables au miroir (ticket scanné en cabine ou parcours digital initié sur le miroir). Aucune commission sur les autres canaux. Reporting transparent hebdomadaire.",
                },
                {
                  q: "Quelle est la durée d'installation ?",
                  a: "Cinq à dix jours ouvrés selon la complexité du point de vente. Calibration biométrique sur place, formation des équipes incluse, mise en service progressive.",
                },
                {
                  q: "Comment est protégée la donnée client ?",
                  a: "Aucune image n'est stockée. Aucune mesure n'est affichée à l'écran. Le jumeau numérique est non identifiant. Conformité RGPD certifiée par notre conseil juridique.",
                },
              ].map((item, i) => (
                <div key={i}>
                  <h3 className="font-display text-white text-[22px] lg:text-[26px] mb-3 leading-tight">
                    <span className="text-[var(--color-or)] mr-3">
                      {String(i + 1).padStart(2, "0")}.
                    </span>
                    {item.q}
                  </h3>
                  <p className="text-white/70 text-[15px] leading-[1.85] pl-9">
                    {item.a}
                  </p>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      <GoldRule className="opacity-30" />

      {/* ==================== CTA FINAL ==================== */}
      <section className="py-24 lg:py-32 relative overflow-hidden">
        <div
          aria-hidden
          className="absolute inset-0 pointer-events-none"
          style={{
            background:
              "radial-gradient(ellipse 60% 60% at 50% 50%, rgba(201,168,76,0.12), transparent 70%)",
          }}
        />
        <div className="container max-w-[1100px] relative z-10 text-center">
          <div className="font-display italic text-[var(--color-or)]/50 text-[80px] lg:text-[140px] leading-none">
            V.
          </div>

          <h2 className="font-display text-white text-[40px] lg:text-[64px] leading-[1.05] mt-6 mb-8">
            Trente maisons. Une seule fois.
            <br />
            <span className="italic text-[var(--color-or)]">
              Réservez votre place.
            </span>
          </h2>

          <p className="text-white/65 text-[17px] leading-[1.7] max-w-[640px] mx-auto mb-12">
            La signature s'opère par voie d'échange direct avec la direction.
            Indiquez votre maison, votre rôle, et un créneau de démonstration —
            nous prenons contact sous 48 heures.
          </p>

          <div className="flex flex-col sm:flex-row items-center justify-center gap-5 mb-10">
            <a
              href={`mailto:${EMAIL}?subject=Offre%20Pionni%C3%A8re%20Divine%202027%20%E2%80%94%20Demande%20de%20d%C3%A9monstration&body=Bonjour%2C%0A%0AJe%20souhaite%20d%C3%A9couvrir%20l%27offre%20pionni%C3%A8re%20Divine%202027%20pour%20la%20maison%20%5BNOM%5D.%0A%0ARole%20%3A%0ACr%C3%A9neau%20souhait%C3%A9%20%3A%0A%0ACordialement%2C%0A`}
              className="btn-or inline-flex"
            >
              Programmer la démonstration <span aria-hidden>→</span>
            </a>
            <Link
              href="/tryon"
              className="text-[12px] tracking-[0.3em] uppercase text-white/70 hover:text-[var(--color-or)] transition-colors border-b border-white/30 hover:border-[var(--color-or)] pb-1"
            >
              Essayer la démo en direct
            </Link>
          </div>

          <div className="font-display italic text-white/40 text-[14px]">
            ou écrire directement à{" "}
            <a
              href={`mailto:${EMAIL}`}
              className="text-[var(--color-or)] hover:text-white transition-colors"
            >
              {EMAIL}
            </a>
          </div>

          <div className="mt-16 flex flex-wrap items-center justify-center gap-x-8 gap-y-3 text-[10px] tracking-[0.32em] uppercase text-white/30">
            <span>Brevet {PATENT}</span>
            <span>·</span>
            <span>SIREN {SIREN}</span>
            <span>·</span>
            <span>LS Compta · Qonto</span>
          </div>
        </div>
      </section>

      <SiteFooter />
    </div>
  );
}
