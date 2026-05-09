/**
 * TRYONYOU — /footscan
 *
 * Foot scan experience: scan progress + foot wireframe + recommendation.
 * Procedural SVG foot silhouette, no real measurements (per project policy).
 */

import { useEffect, useState } from "react";
import { Link } from "wouter";
import SiteHeader from "@/components/sections/SiteHeader";
import SiteFooter from "@/components/sections/SiteFooter";

const RECOMMENDED = [
  { brand: "Atelier Nuit", model: "Mocassin Velours", price: 480, drape: "Cuir lisse · Mat" },
  { brand: "Maison Dorée", model: "Slipper Or", price: 620, drape: "Cuir verni · Or rosé" },
  { brand: "Urban Atelier", model: "Sneaker Clean", price: 320, drape: "Cuir grainé · Ivoire" },
];

function FootSVG() {
  // Stylized golden foot top-down silhouette
  return (
    <svg viewBox="0 0 240 480" className="w-full h-full">
      <defs>
        <linearGradient id="footG" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor="#C9A84C" stopOpacity="0.85" />
          <stop offset="100%" stopColor="#8a7536" stopOpacity="0.55" />
        </linearGradient>
        <filter id="glowF" x="-30%" y="-30%" width="160%" height="160%">
          <feGaussianBlur stdDeviation="4" />
        </filter>
      </defs>
      <g filter="url(#glowF)" opacity="0.4">
        <path d="M 120 30 Q 180 50 175 130 Q 170 200 165 280 Q 160 380 150 440 Q 130 470 110 470 Q 90 470 75 440 Q 70 380 65 280 Q 60 200 55 130 Q 50 50 120 30 Z" fill="#C9A84C" />
      </g>
      <path
        d="M 120 30 Q 180 50 175 130 Q 170 200 165 280 Q 160 380 150 440 Q 130 470 110 470 Q 90 470 75 440 Q 70 380 65 280 Q 60 200 55 130 Q 50 50 120 30 Z"
        fill="url(#footG)"
        stroke="#C9A84C"
        strokeWidth="1.4"
        strokeOpacity="0.85"
      />
      {/* Toes */}
      <circle cx="120" cy="60" r="14" fill="#C9A84C" opacity="0.7" />
      <circle cx="148" cy="80" r="11" fill="#C9A84C" opacity="0.65" />
      <circle cx="92" cy="80" r="11" fill="#C9A84C" opacity="0.65" />
      <circle cx="160" cy="105" r="9" fill="#C9A84C" opacity="0.6" />
      <circle cx="80" cy="105" r="9" fill="#C9A84C" opacity="0.6" />
      {/* Arch lines */}
      <path d="M 70 240 Q 120 230 170 240" stroke="#C9A84C" strokeWidth="0.8" strokeOpacity="0.5" fill="none" />
      <path d="M 70 280 Q 120 270 170 280" stroke="#C9A84C" strokeWidth="0.8" strokeOpacity="0.5" fill="none" />
      <path d="M 70 320 Q 120 310 170 320" stroke="#C9A84C" strokeWidth="0.8" strokeOpacity="0.5" fill="none" />
      {/* Heel */}
      <ellipse cx="115" cy="430" rx="35" ry="22" fill="#C9A84C" opacity="0.35" />
    </svg>
  );
}

export default function FootScan() {
  const [scanning, setScanning] = useState(false);
  const [progress, setProgress] = useState(0);
  const [done, setDone] = useState(false);

  useEffect(() => {
    if (!scanning) return;
    const id = setInterval(() => {
      setProgress((p) => {
        const next = p + Math.random() * 4 + 2;
        if (next >= 100) {
          clearInterval(id);
          setDone(true);
          return 100;
        }
        return next;
      });
    }, 180);
    return () => clearInterval(id);
  }, [scanning]);

  return (
    <div className="min-h-screen flex flex-col bg-[var(--color-noir)]">
      <SiteHeader />
      <main className="flex-1 pt-32 pb-24">
        <section className="container">
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-10 items-start">
            {/* Left copy */}
            <div className="lg:col-span-5">
              <span className="eyebrow mb-5 inline-flex">Foot Scan · V1</span>
              <h1 className="display-l mb-6">
                Le pied,
                <br />
                <span className="accent-italic">précisément.</span>
              </h1>
              <p className="text-[17px] leading-[1.75] text-[var(--color-ivoire)]/80 mb-8">
                TRYONYOU étend la précision biométrique aux chaussures. Le scan
                FootScan reconstruit la voûte plantaire, la cambrure et la pointure
                réelle — sans mètre ruban, sans mesure manuelle. Le résultat : la
                paire qui s'oublie une fois portée.
              </p>

              <ul className="space-y-3 mb-10">
                {[
                  "Capture biométrique non intrusive du pied",
                  "Empreinte 3D — voûte, cambrure, axe",
                  "Recommandation chaussante par maison partenaire",
                  "Profil mémorisé sous chiffrement AES-256",
                ].map((it) => (
                  <li key={it} className="flex items-start gap-3 text-[14px] text-white/75">
                    <span className="text-[var(--color-or)] mt-0.5">◆</span>
                    {it}
                  </li>
                ))}
              </ul>

              {!scanning && !done && (
                <button onClick={() => setScanning(true)} className="btn-or inline-flex">
                  Démarrer le scan
                  <span aria-hidden>→</span>
                </button>
              )}

              {done && (
                <div className="mt-2">
                  <div className="text-[12px] tracking-[0.22em] uppercase text-[var(--color-or)] mb-3">
                    Profil chaussant établi · Pointure dynamique enregistrée
                  </div>
                  <Link href="/catalogue" className="btn-or inline-flex">
                    Voir les recommandations
                    <span aria-hidden>→</span>
                  </Link>
                </div>
              )}
            </div>

            {/* Right scan visual */}
            <div className="lg:col-span-6 lg:col-start-7">
              <div className="mirror-frame aspect-[3/4] overflow-hidden bg-[var(--color-graphite)] flex items-center justify-center relative">
                <div className="w-2/3 h-full relative">
                  <FootSVG />
                  {/* Scan beam */}
                  {scanning && !done && (
                    <div
                      className="absolute left-0 right-0 h-1 bg-gradient-to-r from-transparent via-[var(--color-or)] to-transparent"
                      style={{
                        top: `${progress}%`,
                        boxShadow: "0 0 20px var(--color-or)",
                        transition: "top 0.18s linear",
                      }}
                    />
                  )}
                </div>

                {/* Status overlay */}
                <div className="absolute top-4 left-4 right-4 flex items-center justify-between text-[10px] tracking-[0.24em] uppercase text-[var(--color-or)]">
                  <span>FootScan · V1</span>
                  <span className="inline-flex items-center gap-2">
                    <span className="w-1.5 h-1.5 rounded-full bg-[var(--color-or)] animate-pulse" />
                    {scanning && !done && `${Math.round(progress)}%`}
                    {done && "PROFIL ÉTABLI"}
                    {!scanning && !done && "EN ATTENTE"}
                  </span>
                </div>

                {scanning && !done && (
                  <div className="absolute bottom-4 left-4 right-4">
                    <div className="text-[10px] tracking-[0.24em] uppercase text-[var(--color-or)]/80 mb-2">
                      Capture en cours…
                    </div>
                    <div className="h-px bg-white/10">
                      <div
                        className="h-full bg-[var(--color-or)] transition-all duration-200"
                        style={{ width: `${progress}%` }}
                      />
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Recommendations */}
          {done && (
            <div className="mt-20">
              <div className="hairline mb-8" />
              <div className="grid grid-cols-1 lg:grid-cols-12 gap-10 mb-10">
                <div className="lg:col-span-6">
                  <span className="eyebrow mb-5 inline-flex">Recommandations</span>
                  <h2 className="display-l">
                    Trois paires
                    <br />
                    <span className="accent-italic">pour votre cambrure.</span>
                  </h2>
                </div>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-3 gap-px bg-[rgba(201,168,76,0.2)]">
                {RECOMMENDED.map((s, i) => (
                  <div key={s.model} className="bg-[var(--color-graphite)] p-8">
                    <div className="text-[10px] tracking-[0.28em] uppercase text-[var(--color-or)]/70 mb-2">
                      Maison {i + 1}
                    </div>
                    <div className="font-display text-[22px] text-[var(--color-ivoire)] mb-2 leading-tight">
                      {s.model}
                    </div>
                    <div className="text-[12px] text-white/55 mb-4">{s.brand}</div>
                    <div className="text-[12px] text-white/60 mb-6">{s.drape}</div>
                    <div className="flex items-baseline justify-between">
                      <span className="text-[10px] tracking-widest uppercase text-white/40">
                        Disponible
                      </span>
                      <span className="font-display text-[var(--color-or)] text-[20px]">
                        € {s.price}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </section>
      </main>
      <SiteFooter />
    </div>
  );
}
