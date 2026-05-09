/**
 * Maison Couture Nocturne — footer.
 * Editorial layout with hairlines, SIREN, patent reference.
 */
export default function SiteFooter() {
  return (
    <footer className="relative bg-[var(--color-noir)] border-t border-[rgba(201,168,76,0.25)] pt-20 pb-12">
      <div className="container">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-12 mb-16">
          <div className="lg:col-span-5">
            <div className="font-display italic text-[var(--color-or)] text-[36px] mb-3">
              TRYONYOU
            </div>
            <p className="text-[14px] leading-[1.7] text-[var(--color-ivoire)]/70 max-w-[40ch]">
              Maison de technologie parisienne. Essayage virtuel breveté pour les
              maisons de mode et le retail enterprise.
            </p>
            <div className="mt-8 space-y-2 text-[12px] tracking-[0.06em] text-[var(--color-fog)]">
              <div>SIREN&nbsp;<span className="text-[var(--color-ivoire)]/85">943 610 196</span></div>
              <div>Brevet&nbsp;<span className="text-[var(--color-ivoire)]/85">PCT/EP2025/067317</span></div>
              <div>Siège&nbsp;<span className="text-[var(--color-ivoire)]/85">Paris · France</span></div>
            </div>
          </div>

          <div className="lg:col-span-2">
            <div className="text-[10px] tracking-[0.28em] uppercase text-[var(--color-or)] mb-5">
              Maison
            </div>
            <ul className="space-y-3 text-[14px]">
              <li><a className="text-[var(--color-ivoire)]/80 hover:text-[var(--color-or)] transition-colors" href="#solution">La solution</a></li>
              <li><a className="text-[var(--color-ivoire)]/80 hover:text-[var(--color-or)] transition-colors" href="#technologie">Technologie</a></li>
              <li><a className="text-[var(--color-ivoire)]/80 hover:text-[var(--color-or)] transition-colors" href="#pilote">Pilote</a></li>
              <li><a className="text-[var(--color-ivoire)]/80 hover:text-[var(--color-or)] transition-colors" href="#demo">Démo live</a></li>
            </ul>
          </div>

          <div className="lg:col-span-2">
            <div className="text-[10px] tracking-[0.28em] uppercase text-[var(--color-or)] mb-5">
              Légal
            </div>
            <ul className="space-y-3 text-[14px]">
              <li><span className="text-[var(--color-ivoire)]/80">Mentions légales</span></li>
              <li><span className="text-[var(--color-ivoire)]/80">Politique RGPD</span></li>
              <li><span className="text-[var(--color-ivoire)]/80">Données biométriques</span></li>
              <li><span className="text-[var(--color-ivoire)]/80">CGU</span></li>
            </ul>
          </div>

          <div className="lg:col-span-3">
            <div className="text-[10px] tracking-[0.28em] uppercase text-[var(--color-or)] mb-5">
              Direction
            </div>
            <a href="mailto:contact@tryonyou.app" className="font-display italic text-[var(--color-or)] text-[20px] hover:text-[var(--color-or-pale)] transition-colors block mb-4">
              contact@tryonyou.app
            </a>
            <p className="text-[13px] leading-[1.7] text-[var(--color-ivoire)]/70">
              Pour toute demande presse, partenariat, ou opportunité commerciale.
              Réponse sous 48 heures ouvrées.
            </p>
          </div>
        </div>

        <div className="hairline mb-8" />

        <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4 text-[11px] tracking-[0.18em] uppercase text-[var(--color-fog)]">
          <span>© {new Date().getFullYear()} TRYONYOU — Tous droits réservés</span>
          <span>Conçu &amp; assemblé à Paris</span>
        </div>
      </div>
    </footer>
  );
}
