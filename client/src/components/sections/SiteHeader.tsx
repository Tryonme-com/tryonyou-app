/**
 * Maison Couture Nocturne — sticky header.
 *
 * Layout strategy:
 *   - Logo (left), four primary route links (center), CTA "Lancer la démo" (right).
 *   - Anchor links (Le problème, La solution, …) move to a "More" dropdown that opens on hover.
 *   - On smaller desktop widths, only the four routes remain inline; on tablet/mobile, the
 *     burger menu surfaces everything.
 */
import { useEffect, useRef, useState } from "react";
import { Link, useLocation } from "wouter";

const ANCHORS = [
  { id: "probleme", label: "Le problème" },
  { id: "solution", label: "La solution" },
  { id: "technologie", label: "Technologie" },
  { id: "pilote", label: "Pilote" },
];

const ROUTES = [
  { href: "/tryon", label: "Try-On" },
  { href: "/catalogue", label: "Catalogue" },
  { href: "/manifeste", label: "Manifeste" },
  { href: "/offre", label: "Offre", accent: true },
];

const SECONDARY_ROUTES = [
  { href: "/cap", label: "CAP — Production" },
  { href: "/footscan", label: "Foot Scan" },
  { href: "/investors", label: "Investors" },
];

export default function SiteHeader() {
  const [scrolled, setScrolled] = useState(false);
  const [open, setOpen] = useState(false);
  const [moreOpen, setMoreOpen] = useState(false);
  const moreCloseTimer = useRef<number | null>(null);
  const [location, setLocation] = useLocation();
  const isHome = location === "/" || location === "";

  useEffect(() => {
    const handler = () => setScrolled(window.scrollY > 30);
    handler();
    window.addEventListener("scroll", handler, { passive: true });
    return () => window.removeEventListener("scroll", handler);
  }, []);

  const goAnchor = (id: string) => (e: React.MouseEvent) => {
    e.preventDefault();
    setOpen(false);
    setMoreOpen(false);
    if (isHome) {
      const el = document.getElementById(id);
      if (el) el.scrollIntoView({ behavior: "smooth", block: "start" });
    } else {
      setLocation("/");
      setTimeout(() => {
        const el = document.getElementById(id);
        if (el) el.scrollIntoView({ behavior: "smooth", block: "start" });
      }, 80);
    }
  };

  const openMore = () => {
    if (moreCloseTimer.current) {
      window.clearTimeout(moreCloseTimer.current);
      moreCloseTimer.current = null;
    }
    setMoreOpen(true);
  };
  const scheduleCloseMore = () => {
    if (moreCloseTimer.current) window.clearTimeout(moreCloseTimer.current);
    moreCloseTimer.current = window.setTimeout(() => setMoreOpen(false), 220);
  };

  return (
    <header
      className={`fixed top-0 inset-x-0 z-50 transition-all duration-700 ${
        scrolled || !isHome
          ? "backdrop-blur-md bg-[rgba(10,8,7,0.82)] border-b border-[rgba(201,168,76,0.25)]"
          : "bg-transparent"
      }`}
    >
      <div className="container flex items-center justify-between h-[72px] md:h-[80px] gap-4">
        <Link
          href="/"
          className="group flex items-center gap-3 shrink-0"
          onClick={() => setOpen(false)}
        >
          <span
            className="text-[var(--color-or)] font-display italic tracking-tight text-[22px] md:text-[24px] leading-none"
            style={{ fontFamily: "var(--font-display)" }}
          >
            TRYONYOU
          </span>
        </Link>

        <nav className="hidden lg:flex items-center gap-6 xl:gap-8">
          {ROUTES.map((r) => (
            <Link
              key={r.href}
              href={r.href}
              className={`text-[11px] tracking-[0.22em] uppercase whitespace-nowrap transition-colors duration-500 ${
                location.startsWith(r.href)
                  ? "text-[var(--color-or)]"
                  : (r as any).accent
                  ? "text-[var(--color-or)] hover:text-white"
                  : "text-[var(--color-ivoire)]/80 hover:text-[var(--color-or)]"
              }`}
            >
              {r.label}
            </Link>
          ))}

          {/* "More" dropdown for the home page anchors */}
          <div
            className="relative"
            onMouseEnter={openMore}
            onMouseLeave={scheduleCloseMore}
          >
            <button
              type="button"
              onClick={() => setMoreOpen((s) => !s)}
              className="text-[11px] tracking-[0.22em] uppercase whitespace-nowrap text-[var(--color-ivoire)]/65 hover:text-[var(--color-or)] transition-colors duration-500 flex items-center gap-1"
              aria-expanded={moreOpen}
              aria-haspopup="menu"
            >
              Maison
              <span
                className={`text-[8px] transition-transform duration-300 ${
                  moreOpen ? "rotate-180" : ""
                }`}
                aria-hidden
              >
                ▾
              </span>
            </button>
            {moreOpen && (
              <div
                role="menu"
                className="absolute right-0 top-[calc(100%+10px)] min-w-[220px] bg-[rgba(10,8,7,0.96)] backdrop-blur-md border border-[rgba(201,168,76,0.25)] rounded-sm shadow-2xl py-2"
                onMouseEnter={openMore}
                onMouseLeave={scheduleCloseMore}
              >
                {SECONDARY_ROUTES.map((r) => (
                  <Link
                    key={r.href}
                    href={r.href}
                    onClick={() => setMoreOpen(false)}
                    className="block px-4 py-2.5 text-[11px] tracking-[0.22em] uppercase text-[var(--color-ivoire)]/75 hover:text-[var(--color-or)] hover:bg-[rgba(201,168,76,0.06)] transition-colors duration-300"
                    role="menuitem"
                  >
                    {r.label}
                  </Link>
                ))}
                <div className="my-1 border-t border-[rgba(201,168,76,0.15)]" />
                {ANCHORS.map((a) => (
                  <a
                    key={a.id}
                    href={`#${a.id}`}
                    onClick={goAnchor(a.id)}
                    className="block px-4 py-2.5 text-[11px] tracking-[0.22em] uppercase text-[var(--color-ivoire)]/75 hover:text-[var(--color-or)] hover:bg-[rgba(201,168,76,0.06)] transition-colors duration-300"
                    role="menuitem"
                  >
                    {a.label}
                  </a>
                ))}
              </div>
            )}
          </div>
        </nav>

        <div className="hidden lg:flex shrink-0">
          <Link href="/tryon" className="btn-or whitespace-nowrap text-[11px] tracking-[0.22em] !px-5 !py-2.5">
            Lancer la démo
          </Link>
        </div>

        <button
          aria-label="Menu"
          className="lg:hidden text-[var(--color-or)] shrink-0"
          onClick={() => setOpen((s) => !s)}
        >
          <svg width="28" height="28" viewBox="0 0 28 28" fill="none">
            <path
              d={open ? "M6 6 L22 22 M22 6 L6 22" : "M4 8 L24 8 M4 14 L24 14 M4 20 L24 20"}
              stroke="currentColor"
              strokeWidth="1.4"
              strokeLinecap="square"
            />
          </svg>
        </button>
      </div>

      {/* Mobile sheet */}
      <div
        className={`lg:hidden overflow-hidden transition-[max-height] duration-700 ${
          open ? "max-h-[90vh]" : "max-h-0"
        }`}
      >
        <div className="container py-6 border-t border-[rgba(201,168,76,0.2)] bg-[var(--color-noir)]/95 backdrop-blur-md">
          <ul className="flex flex-col gap-3">
            {[...ROUTES, ...SECONDARY_ROUTES].map((r) => (
              <li key={r.href}>
                <Link
                  href={r.href}
                  className="block text-[14px] tracking-[0.18em] uppercase text-[var(--color-or)] py-2"
                  onClick={() => setOpen(false)}
                >
                  {r.label}
                </Link>
              </li>
            ))}
            <li className="my-2 hairline" />
            {ANCHORS.map((a) => (
              <li key={a.id}>
                <a
                  href={`#${a.id}`}
                  onClick={goAnchor(a.id)}
                  className="block text-[14px] tracking-[0.18em] uppercase text-[var(--color-ivoire)]/80 py-2"
                >
                  {a.label}
                </a>
              </li>
            ))}
            <li className="pt-3">
              <Link
                href="/tryon"
                className="btn-or w-full justify-center"
                onClick={() => setOpen(false)}
              >
                Lancer la démo
              </Link>
            </li>
          </ul>
        </div>
      </div>
    </header>
  );
}
